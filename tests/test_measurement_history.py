from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from config.settings import SENSORS
from data.measurement_history import MeasurementHistory
from data.scenarios.factory_machine import Factory
from detection.detector import AnomalyDetector
from detection.detection_history import DetectionHistory
from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool


class MeasurementHistoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.history = MeasurementHistory.create(self.directory.name)
        self.start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.machine = Factory.create(start_time=self.start, step_duration=timedelta(seconds=2))
        self.rows = []
        for _ in range(6):
            row = self.machine.step()
            self.history.append(row)
            self.rows.append(row)

    def test_round_trip_and_simulated_clock(self):
        rows = [json.loads(line) for line in self.history.path.read_text().splitlines()]
        self.assertEqual(rows, self.rows)
        self.assertEqual(rows[-1]['timestamp'], '2026-01-01T00:00:10+00:00')
        self.assertEqual(MeasurementHistory(self.history.path).select(), rows)

    def test_latest_and_alert_cutoff(self):
        self.assertEqual(self.history.select(n_points=5), self.rows[-5:])
        self.assertEqual(self.history.select(self.rows[3]['timestamp'], 3), self.rows[1:4])
        self.assertEqual(self.history.select(n_points=100), self.rows)
        self.assertEqual(self.history.select('2026-01-01T00:00:05+00:00', 2), self.rows[1:3])
        self.assertEqual(self.history.select('2026-01-01T01:00:04+01:00', 1), self.rows[2:3])

    def test_inclusive_centered_and_partial_windows(self):
        self.assertEqual(self.history.select(self.rows[2]['timestamp'], before_seconds=2,
                                             after_seconds=2), self.rows[1:4])
        self.assertEqual(self.history.select(self.rows[-1]['timestamp'], before_seconds=2,
                                             after_seconds=100), self.rows[-2:])
        self.assertEqual(self.history.select(self.rows[0]['timestamp'], before_seconds=100), self.rows[:1])

    def test_empty_window_and_single_sample(self):
        before = '2025-12-31T00:00:00+00:00'
        self.assertEqual(self.history.select(before), [])
        self.assertEqual(HistoryTool(self.history).run(['temperature'], timestamp=before)['timestamp'], [])
        stats = StatisticsTool(self.history).run(before)
        self.assertEqual(stats['window']['count'], 0)
        self.assertIsNone(stats['temperature']['mean'])
        self.assertIsNone(stats['temperature']['delta'])
        single = StatisticsTool(self.history).run(n_points=1)
        self.assertIsNone(single['temperature']['std'])
        self.assertEqual(single['temperature']['delta'], 0)
        json.dumps(single, allow_nan=False)

    def test_tools_share_exact_window(self):
        args = dict(timestamp=self.rows[3]['timestamp'], n_points=3)
        history = HistoryTool(self.history).run(["temperature", "vibration"], **args)
        statistics = StatisticsTool(self.history).run(**args)
        self.assertEqual(history['timestamp'], [r['timestamp'] for r in self.rows[1:4]])
        self.assertEqual(statistics['window']['count'], 3)
        for sensor in ("temperature", "vibration"):
            self.assertAlmostEqual(statistics[sensor]['mean'], sum(history[sensor]) / 3)
            self.assertEqual(statistics[sensor]['delta'], history[sensor][-1] - history[sensor][0])
            self.assertNotIn('slope', statistics[sensor])
        window = StatisticsTool(self.history).run(self.rows[2]['timestamp'], before_seconds=2, after_seconds=2)
        self.assertEqual(window['window']['start'], self.rows[1]['timestamp'])
        self.assertEqual(window['window']['end'], self.rows[3]['timestamp'])

    def test_invalid_queries_and_clock(self):
        for kwargs in ({'n_points': 0}, {'n_points': -1}, {'n_points': True},
                       {'timestamp': '2026-01-01'}, {'before_seconds': 5},
                       {'after_seconds': 1}, {'before_seconds': -1},
                       {'before_seconds': float('nan')}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.history.select(**kwargs)
        with self.assertRaises(ValueError):
            Factory.create(start_time=datetime(2026, 1, 1))
        with self.assertRaises(ValueError):
            Factory.create(step_duration=timedelta(0))

    def test_runs_are_isolated(self):
        other = MeasurementHistory.create(self.directory.name)
        self.assertNotEqual(other.path, self.history.path)
        self.assertEqual(other.select(), [])
        self.assertEqual(len(self.history.select()), 6)

    def test_invalid_data_is_not_written(self):
        initial = self.history.path.read_bytes()
        with self.assertRaises(ValueError):
            self.history.append({**self.rows[-1], 'temperature': float('nan')})
        self.assertEqual(self.history.path.read_bytes(), initial)

    def test_corrupt_or_unordered_history_fails_explicitly(self):
        self.history.append(self.rows[0])
        with self.assertRaisesRegex(ValueError, 'Non-increasing'):
            self.history.select()
        other = MeasurementHistory.create(self.directory.name)
        other.path.write_text('{unfinished')
        with self.assertRaises(json.JSONDecodeError):
            other.select()

    def test_detection_log_accepts_timestamp_contract(self):
        signal = AnomalyDetector(threshold=0).detect(self.rows[-1])
        log = DetectionHistory()
        log.path = Path(self.directory.name) / 'alerts' / 'detections.jsonl'
        log.save(signal)
        saved = json.loads(log.path.read_text())
        self.assertEqual(saved['timestamp'], self.rows[-1]['timestamp'])

    def test_main_persists_before_detection_and_shares_history(self):
        import main
        history = MeasurementHistory.create(self.directory.name)
        detector = AnomalyDetector(threshold=0)

        def detect(sensor_values):
            self.assertEqual(history.select(n_points=1), [sensor_values])
            return detector.detect(sensor_values)

        def investigate(context, agent, registry):
            for name in ('history', 'statistics'):
                self.assertIs(registry.get(name).history, history)
            self.assertEqual(registry.get('history').run(['temperature'], context.request.timestamp, 1)['timestamp'],
                             [context.request.timestamp])
            # Isolate the unrelated LangGraph final-result contract.
            return SimpleNamespace(final_conclusion='offline', observations=[], hypotheses=[],
                                   status='completed', stop_reason='agent_finished', error_message=None)

        with patch.object(main.MeasurementHistory, 'create', return_value=history), \
             patch.object(main, 'LLMAgent'), \
             patch.object(main, 'AnomalyDetector', return_value=SimpleNamespace(detect=detect)), \
             patch.object(main, 'run_investigation', side_effect=investigate), \
             patch('requests.post', side_effect=AssertionError('Network is forbidden')), \
             redirect_stdout(StringIO()):
            main.main()
        self.assertEqual(len(history.select()), 1)


if __name__ == '__main__':
    unittest.main()
