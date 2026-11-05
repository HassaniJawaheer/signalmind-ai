import unittest
from unittest.mock import patch

from config import settings
from detection.detector import AnomalyDetector


class DetectionTests(unittest.TestCase):
    def measurement(self, **values):
        data = {
            'temperature': 55.0,
            'rotational_speed': 2900.0,
            'power_consumption': 1.105,
            'pressure': 1.962,
            'flow_rate': 12.0,
            'timestamp': '2026-01-01T00:00:00+00:00',
        }
        data.update(values)
        return data

    def test_configured_threshold_controls_trigger(self):
        measurement = self.measurement(temperature=90)
        with patch.object(settings, 'ANOMALY_SCORE_THRESHOLD', 5):
            signal = AnomalyDetector().detect(measurement)
            self.assertEqual(signal.score, 5)
            self.assertTrue(signal.trigger)
        with patch.object(settings, 'ANOMALY_SCORE_THRESHOLD', 6):
            self.assertFalse(AnomalyDetector().detect(measurement).trigger)

    def test_explicit_threshold_overrides_configuration(self):
        with patch.object(settings, 'ANOMALY_SCORE_THRESHOLD', 9):
            self.assertEqual(AnomalyDetector(threshold=4).threshold, 4)
            self.assertEqual(AnomalyDetector(threshold=0).threshold, 0)

    def test_normal_low_speed_is_not_a_low_flow_fault(self):
        signal = AnomalyDetector().detect(self.measurement(
            rotational_speed=1450, flow_rate=6, pressure=0.4905,
        ))
        self.assertEqual(signal.score, 0)
        self.assertFalse(signal.trigger)
        stopped = AnomalyDetector().detect(self.measurement(
            rotational_speed=0, flow_rate=0, pressure=0,
        ))
        self.assertFalse(stopped.trigger)

    def test_restriction_signature_triggers(self):
        signal = AnomalyDetector().detect(self.measurement(flow_rate=6.93, pressure=2.616))
        self.assertEqual(signal.score, 5)
        self.assertTrue(signal.trigger)


if __name__ == '__main__':
    unittest.main()
