import json
import os
import unittest
from unittest.mock import Mock, patch

import requests

from investigation.agents.groq_client import GroqClient
from investigation.agents.llm_agent import LLMAgent
from investigation.agents.output_parser import OutputParser
from investigation.errors import InvestigationError
from investigation.langgraph.graph import run_investigation
from investigation.models.agent_action import AgentAction
from investigation.models.context import Context
from investigation.models.request import Request
from investigation.models.results import InvestigationResult
from investigation.runtime import InvestigationRuntime
from investigation.tools.tool_registry import ToolRegistry


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.network = patch('requests.post', side_effect=AssertionError('Real network forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)

    def context(self):
        return Context(Request('2026-01-01T00:00:00+00:00', {}))

    def finish(self):
        return AgentAction('finish', 'Final observation.', 'Final hypothesis.', final_conclusion='Conclusion.')

    def call(self):
        return AgentAction('call_tool', 'First observation.', 'First hypothesis.', 'analysis', {'value': 3})

    def registry(self, failing=False):
        class Tool:
            name = 'analysis'

            def run(self, value):
                if failing:
                    raise ValueError('sensitive internal details')
                return {'value': value}

        registry = ToolRegistry()
        registry.register(Tool())
        return registry

    def run_case(self, graph, agent, registry=None, **limits):
        if registry is None:
            registry = self.registry()
        if graph:
            return run_investigation(self.context(), agent, registry, **limits)
        return InvestigationRuntime(agent, registry, **limits).run(self.context())

    def test_immediate_finish(self):
        for graph in (False, True):
            with self.subTest(graph=graph):
                result = self.run_case(graph, Mock(decide=Mock(return_value=self.finish())))
                self.assertIsInstance(result, InvestigationResult)
                self.assertEqual(result.status, 'completed')
                self.assertEqual(result.stop_reason, 'agent_finished')
                self.assertEqual(result.final_conclusion, 'Conclusion.')
                self.assertEqual(result.observations, ['Final observation.'])
                self.assertEqual(result.hypotheses, ['Final hypothesis.'])
                self.assertIsNone(result.error_message)

    def test_tool_then_finish_without_duplicates(self):
        for graph in (False, True):
            agent = Mock(decide=Mock(side_effect=[self.call(), self.finish()]))
            result = self.run_case(graph, agent)
            self.assertEqual(result.observations, ['First observation.', 'Final observation.'])
            self.assertEqual(len(result.hypotheses), 2)
            self.assertEqual(len(result.tool_calls), 1)
            self.assertEqual(result.tool_calls[0].tool_output, {'value': 3})
            self.assertEqual(result.status, 'completed')

    def test_api_failure_preserves_previous_work(self):
        for graph in (False, True):
            agent = Mock(decide=Mock(side_effect=[self.call(), InvestigationError('api_timeout', 'The API request timed out.')]))
            result = self.run_case(graph, agent)
            self.assertEqual(result.status, 'failed')
            self.assertEqual(result.stop_reason, 'api_timeout')
            self.assertEqual(result.observations, ['First observation.'])
            self.assertEqual(len(result.tool_calls), 1)
            self.assertIsNone(result.final_conclusion)
            self.assertEqual(agent.decide.call_count, 2)

    def test_invalid_actions(self):
        actions = [
            AgentAction('unknown', '', ''),
            AgentAction('finish', '', '', final_conclusion=''),
            AgentAction('finish', [], '', final_conclusion='Conclusion'),
            AgentAction('call_tool', '', ''),
            AgentAction('call_tool', '', '', 'analysis', []),
        ]
        for graph in (False, True):
            for action in actions:
                with self.subTest(graph=graph, action=action):
                    result = self.run_case(graph, Mock(decide=Mock(return_value=action)))
                    self.assertEqual(result.status, 'failed')
                    self.assertEqual(result.stop_reason, 'invalid_action')
                    self.assertIsNone(result.final_conclusion)

    def test_tool_errors(self):
        for graph in (False, True):
            result = self.run_case(graph, Mock(decide=Mock(return_value=self.call())), self.registry(failing=True))
            self.assertEqual(result.stop_reason, 'tool_error')
            self.assertNotIn('sensitive', result.error_message)
            self.assertEqual(result.observations, ['First observation.'])
            for action in (
                AgentAction('call_tool', '', '', 'missing'),
                AgentAction('call_tool', '', '', 'analysis', {'wrong': 3}),
            ):
                result = self.run_case(graph, Mock(decide=Mock(return_value=action)))
                self.assertEqual(result.stop_reason, 'invalid_tool_call')

    def test_iteration_limit_and_graph_recursion_margin(self):
        for graph in (False, True):
            agent = Mock(decide=Mock(return_value=self.call()))
            result = self.run_case(graph, agent, max_iterations=15)
            self.assertEqual(result.status, 'incomplete')
            self.assertEqual(result.stop_reason, 'iteration_limit')
            self.assertEqual(agent.decide.call_count, 15)
            self.assertEqual(len(result.tool_calls), 15)
            self.assertIsNone(result.final_conclusion)

    def test_duration_limit_before_first_decision(self):
        for graph in (False, True):
            agent = Mock()
            with patch('investigation.runtime.monotonic', side_effect=[0, 2]):
                result = self.run_case(graph, agent, max_duration_seconds=1)
            self.assertEqual(result.stop_reason, 'duration_limit')
            self.assertEqual(result.status, 'incomplete')
            agent.decide.assert_not_called()

    def test_duration_limit_after_decision_preserves_observations(self):
        for graph in (False, True):
            with patch('investigation.runtime.monotonic', side_effect=[0, 0, 2]):
                result = self.run_case(graph, Mock(decide=Mock(return_value=self.finish())), max_duration_seconds=1)
            self.assertEqual(result.status, 'incomplete')
            self.assertEqual(result.observations, ['Final observation.'])
            self.assertIsNone(result.final_conclusion)

    def test_duration_limit_after_tool_preserves_output(self):
        for graph in (False, True):
            with patch('investigation.runtime.monotonic', side_effect=[0, 0, 0, 0, 2]):
                result = self.run_case(graph, Mock(decide=Mock(return_value=self.call())), max_duration_seconds=1)
            self.assertEqual(result.stop_reason, 'duration_limit')
            self.assertEqual(len(result.tool_calls), 1)

    def test_unexpected_agent_failure_is_safe(self):
        for graph in (False, True):
            agent = Mock(decide=Mock(side_effect=RuntimeError('secret-key')))
            result = self.run_case(graph, agent)
            self.assertEqual(result.stop_reason, 'agent_error')
            self.assertNotIn('secret-key', result.error_message)

    def test_graph_runs_are_isolated(self):
        first = self.run_case(True, Mock(decide=Mock(side_effect=[self.call(), self.finish()])))
        second = self.run_case(True, Mock(decide=Mock(return_value=self.finish())))
        self.assertEqual(len(first.tool_calls), 1)
        self.assertEqual(second.tool_calls, [])

    def test_invalid_limits(self):
        for limits in ({'max_iterations': 0}, {'max_iterations': True},
                       {'max_duration_seconds': 0}, {'max_duration_seconds': float('nan')}):
            with self.assertRaises(ValueError):
                InvestigationRuntime(Mock(), self.registry(), **limits)


class ApiTests(unittest.TestCase):
    def setUp(self):
        pacing = patch('config.settings.GROQ_MIN_CALL_INTERVAL_SECONDS', 0)
        pacing.start()
        self.addCleanup(pacing.stop)
        environment = patch.dict(os.environ, {'GROQ_API_KEY': 'secret-key', 'GROQ_MODEL': 'test-model'})
        environment.start()
        self.addCleanup(environment.stop)
        self.client = GroqClient(connect_timeout=2, read_timeout=7)

    def test_success_and_timeout_configuration(self):
        response = Mock(ok=True)
        response.json.return_value = {'choices': [{'message': {'content': 'answer'}}]}
        with patch('requests.post', return_value=response) as post:
            self.assertEqual(self.client.generate('prompt'), 'answer')
        post.assert_called_once()
        self.assertEqual(post.call_args.kwargs['timeout'], (2, 7))

    def test_network_failures_without_retry(self):
        for error, reason in ((requests.Timeout('secret-key'), 'api_timeout'),
                              (requests.ConnectionError('secret-key'), 'network_error'),
                              (requests.RequestException('secret-key'), 'api_error')):
            with patch('requests.post', side_effect=error) as post:
                with self.assertRaises(InvestigationError) as caught:
                    self.client.generate('prompt')
            self.assertEqual(caught.exception.reason, reason)
            self.assertNotIn('secret-key', caught.exception.message)
            post.assert_called_once()

    def test_http_failure_classification(self):
        cases = [
            (400, 'context_length_exceeded', 'context_limit'),
            (429, 'insufficient_quota', 'quota_exceeded'),
            (429, None, 'rate_limit'),
            (401, None, 'authentication_error'),
            (500, None, 'api_error'),
            (400, None, 'api_error'),
        ]
        for status, code, reason in cases:
            response = Mock(ok=False, status_code=status)
            response.json.return_value = {'error': {'code': code, 'message': 'secret-key'}}
            with patch('requests.post', return_value=response) as post:
                with self.assertRaises(InvestigationError) as caught:
                    self.client.generate('prompt')
            self.assertEqual(caught.exception.reason, reason)
            self.assertNotIn('secret-key', caught.exception.message)
            post.assert_called_once()

    def test_malformed_api_responses(self):
        for payload in ({}, {'choices': []}, {'choices': [{'message': {'content': None}}]}):
            response = Mock(ok=True)
            response.json.return_value = payload
            with patch('requests.post', return_value=response):
                with self.assertRaises(InvestigationError) as caught:
                    self.client.generate('prompt')
            self.assertEqual(caught.exception.reason, 'invalid_response')

    def test_real_agent_with_mocked_http_and_real_graph(self):
        registry = ToolRegistry()
        response = Mock(ok=True)
        response.json.return_value = {'choices': [{'message': {'content': json.dumps({
            'action_type': 'finish', 'observations': 'Observed.', 'hypotheses': 'Possible cause.',
            'final_conclusion': 'Done.',
        })}}]}
        with patch('requests.post', return_value=response) as post:
            result = run_investigation(Context(Request('2026-01-01T00:00:00+00:00', {})), LLMAgent(registry), registry)
        self.assertEqual(result.status, 'completed')
        self.assertEqual(result.final_conclusion, 'Done.')
        post.assert_called_once()

    def test_real_agent_failures_finalize_without_retry(self):
        registry = ToolRegistry()
        for failure in ('timeout', 'invalid_json', 'context_limit'):
            response = Mock(ok=True)
            response.json.return_value = {'choices': [{'message': {'content': 'not JSON'}}]}
            expected = 'invalid_response'
            if failure == 'context_limit':
                response.ok = False
                response.status_code = 400
                response.json.return_value = {'error': {'code': 'context_length_exceeded'}}
                expected = 'context_limit'
            with patch('requests.post', return_value=response) as post:
                if failure == 'timeout':
                    post.side_effect = requests.Timeout('private response details')
                    expected = 'api_timeout'
                result = run_investigation(
                    Context(Request('2026-01-01T00:00:00+00:00', {})),
                    LLMAgent(registry), registry,
                )
            self.assertEqual(result.status, 'failed')
            self.assertEqual(result.stop_reason, expected)
            self.assertIsNone(result.final_conclusion)
            post.assert_called_once()

    def test_non_json_http_error_uses_generic_reason(self):
        response = Mock(ok=False, status_code=502)
        response.json.side_effect = ValueError('private response details')
        with patch('requests.post', return_value=response):
            with self.assertRaises(InvestigationError) as caught:
                self.client.generate('prompt')
        self.assertEqual(caught.exception.reason, 'api_error')
        self.assertEqual(caught.exception.message, 'The API returned HTTP 502.')

    def test_invalid_json_and_shape(self):
        for output, reason in (('not JSON', 'invalid_response'), ('[]', 'invalid_action'),
                               ('{}', 'invalid_action')):
            with self.assertRaises(InvestigationError) as caught:
                OutputParser().parse(output)
            self.assertEqual(caught.exception.reason, reason)


if __name__ == '__main__':
    unittest.main()
