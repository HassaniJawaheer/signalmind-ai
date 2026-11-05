from copy import deepcopy
from datetime import datetime, timedelta, timezone
import tempfile
import unittest
from unittest.mock import Mock, patch

from config import settings
from data.measurement_history import MeasurementHistory
from investigation.models.context import Context
from investigation.models.request import Request
from investigation.models.agent_action import AgentAction
from investigation.models.tool_call import ToolCall
from investigation.prompts.context_formatter import ContextFormatter
from investigation.prompts.tool_output_formatter import ToolOutputFormatter
from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool
from investigation.tools.tool_registry import ToolRegistry
from investigation.langgraph.graph import run_investigation


class PromptLimitsTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.history = MeasurementHistory.create(directory.name)
        self.rows = []
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for index in range(1100):
            row = {sensor: index + 0.123456789 for sensor in settings.SENSORS}
            row['timestamp'] = (start + timedelta(seconds=index)).isoformat()
            self.history.append(row)
            self.rows.append(row)

    def test_raw_caps_for_count_and_time_window(self):
        tool = HistoryTool(self.history)
        for arguments in (
            {'n_points': 1100},
            {'timestamp': self.rows[-1]['timestamp'], 'before_seconds': 2000},
        ):
            result = tool.run(['temperature', 'pressure'], **arguments)
            self.assertEqual(set(result), {'window', 'temperature', 'pressure', 'timestamp'})
            self.assertEqual(result['temperature'], [r['temperature'] for r in self.rows[-15:]])
            self.assertEqual(result['window']['selected_count'], 1100)
            self.assertTrue(result['window']['truncated'])
            self.assertEqual(result['window']['count'], 15)
        self.assertEqual(len(tool.run(['temperature'])['temperature']), 15)
        self.assertFalse(tool.run(['temperature'], n_points=10)['window']['truncated'])

    def test_sensor_validation(self):
        for sensors in ([], ['temperature', 'rotational_speed', 'pressure'], ['bad'],
                        ['temperature', 'temperature'], 'temperature'):
            with self.subTest(sensors=sensors), self.assertRaises(ValueError):
                HistoryTool(self.history).run(sensors)

    def test_analysis_cap_and_statistics_are_separate(self):
        stats = StatisticsTool(self.history).run(n_points=1100)
        self.assertEqual(stats['window']['count'], 1000)
        self.assertTrue(stats['window']['truncated'])
        self.assertAlmostEqual(stats['temperature']['mean'], 599.623456789)
        with patch.object(settings, 'MAX_ANALYSIS_POINTS', 20):
            with patch.object(settings, 'MAX_HISTORY_POINTS', 5):
                self.assertEqual(len(self.history.select(n_points=1100)), 20)
                self.assertEqual(StatisticsTool(self.history).run(
                    self.rows[-1]['timestamp'], before_seconds=2000)['window']['count'], 20)
                self.assertEqual(len(HistoryTool(self.history).run(['temperature'], n_points=1100)['timestamp']), 5)
        self.assertEqual(len(self.history.path.read_text().splitlines()), 1100)

    def test_rounding_does_not_mutate_evidence(self):
        output = {'value': 1.1234567, 'list': [2.987654], 'window': {'count': 10}}
        original = deepcopy(output)
        with patch.object(settings, 'PROMPT_DECIMAL_PLACES', 3):
            text = ToolOutputFormatter().format(output)
        self.assertIn('1.123', text)
        self.assertNotIn('1.1234567', text)
        self.assertIn('2.988', text)
        self.assertEqual(output, original)

    def test_window_uses_turn_numbers_not_list_positions(self):
        context = Context(Request(self.rows[-1]['timestamp'], self.rows[-1]))
        context.iterations = 7
        context.observations = ['old-observation', 'recent-observation']
        context.observation_turns = [1, 5]
        context.hypotheses = ['old-hypothesis', 'recent-hypothesis']
        context.hypothesis_turns = [2, 6]
        context.tool_calls = [ToolCall('test', {}, {'evidence': 'old-output'}, turn=2),
                              ToolCall('test', {}, {'evidence': 'recent-output'}, turn=3)]
        original = deepcopy(context)
        text = ContextFormatter().format(context)
        for old in ('old-observation', 'old-hypothesis', 'old-output'):
            self.assertNotIn(old, text)
        for recent in ('recent-observation', 'recent-hypothesis', 'recent-output'):
            self.assertIn(recent, text)
        self.assertIn(context.request.timestamp, text)
        self.assertEqual(context, original)

    def test_real_graph_keeps_trace_but_bounds_prompt(self):
        registry = ToolRegistry()
        registry.register(HistoryTool(self.history))
        prompts = []
        formatter = ContextFormatter()

        def decide(context):
            prompts.append(formatter.format(context))
            if context.iterations == 9:
                return AgentAction('finish', 'last observation', '', final_conclusion='Done')
            return AgentAction('call_tool', f'observation-{context.iterations}', '',
                               'history', {'sensors': ['temperature'], 'n_points': 100})

        with patch('requests.sessions.Session.request', side_effect=AssertionError('Network forbidden')):
            result = run_investigation(
                Context(Request(self.rows[-1]['timestamp'], self.rows[-1])),
                Mock(decide=Mock(side_effect=decide)), registry,
            )
        self.assertEqual(result.status, 'completed')
        self.assertEqual(len(result.tool_calls), 8)
        self.assertEqual(len(result.observations), 9)
        self.assertNotIn('observation-1', prompts[-1])
        self.assertIn('observation-5', prompts[-1])
        self.assertNotIn('observation-4', prompts[-1])
        self.assertLess(abs(len(prompts[-1]) - len(prompts[4])), 30)
        self.assertEqual([call.turn for call in result.tool_calls], list(range(1, 9)))


if __name__ == '__main__':
    unittest.main()
