import json
import unittest
from unittest.mock import Mock

from investigation.agents.output_parser import OutputParser
from investigation.langgraph.graph import run_investigation
from investigation.models.agent_action import AgentAction
from investigation.models.context import Context
from investigation.models.request import Request
from investigation.prompts.context_formatter import ContextFormatter
from investigation.prompts.output_schema import OUTPUT_SCHEMA
from investigation.runtime import InvestigationRuntime
from investigation.tools.tool_registry import ToolRegistry


class FinishPromptTests(unittest.TestCase):
    def test_actual_budget_reaches_prompt_in_both_runners(self):
        for use_graph in (False, True):
            registry = ToolRegistry()
            tool = Mock()
            tool.name = 'analysis'
            tool.run = lambda: {'value': 1}
            registry.register(tool)
            prompts = []

            def decide(context):
                prompts.append(ContextFormatter().format(context))
                if context.iterations == 3:
                    return AgentAction('finish', '', '', final_conclusion='Cause undetermined.')
                return AgentAction('call_tool', '', '', 'analysis', {})

            agent = Mock(decide=decide)
            context = Context(Request('2026-01-01T00:00:00+00:00', {}))
            if use_graph:
                result = run_investigation(context, agent, registry, max_iterations=3)
            else:
                result = InvestigationRuntime(agent, registry, max_iterations=3).run(context)
            self.assertIn('Decision 1 of 3. 2 decisions remaining', prompts[0])
            self.assertIn('Decision 2 of 3. 1 decisions remaining', prompts[1])
            self.assertNotIn('last decision:', prompts[1])
            self.assertIn('Decision 3 of 3. 0 decisions remaining', prompts[2])
            self.assertIn('last decision: return finish', prompts[2])
            self.assertEqual(result.status, 'completed')
            self.assertEqual(result.final_conclusion, 'Cause undetermined.')

    def test_examples_match_action_contract(self):
        examples = [line for line in OUTPUT_SCHEMA.splitlines() if line.startswith('{')]
        self.assertEqual(len(examples), 2)
        actions = [OutputParser().parse(line) for line in examples]
        self.assertEqual([action.action_type for action in actions], ['call_tool', 'finish'])

    def test_noncompliance_does_not_fabricate_conclusion(self):
        registry = ToolRegistry()
        tool = Mock()
        tool.name = 'analysis'
        tool.run = lambda: {}
        registry.register(tool)
        agent = Mock(decide=Mock(return_value=AgentAction('call_tool', '', '', 'analysis', {})))
        result = run_investigation(Context(Request('2026-01-01T00:00:00+00:00', {})),
                                   agent, registry, max_iterations=1)
        self.assertEqual(result.status, 'incomplete')
        self.assertEqual(result.stop_reason, 'iteration_limit')
        self.assertIsNone(result.final_conclusion)


if __name__ == '__main__':
    unittest.main()
