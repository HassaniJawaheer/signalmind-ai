import unittest
from unittest.mock import patch

from config import settings
from detection.detector import AnomalyDetector


class DetectionTests(unittest.TestCase):
    def test_configured_threshold_controls_trigger(self):
        measurement = {
            "temperature": 90.0,
            "vibration": 0.1,
            "pressure": 0.5,
            "flow_rate": 0.5,
            "timestamp": "2026-01-01T00:00:00+00:00",
        }
        with patch.object(settings, "ANOMALY_SCORE_THRESHOLD", 2):
            signal = AnomalyDetector().detect(measurement)
            self.assertEqual(signal.score, 2)
            self.assertTrue(signal.trigger)
        with patch.object(settings, "ANOMALY_SCORE_THRESHOLD", 3):
            self.assertFalse(AnomalyDetector().detect(measurement).trigger)

    def test_explicit_threshold_overrides_configuration(self):
        with patch.object(settings, "ANOMALY_SCORE_THRESHOLD", 9):
            self.assertEqual(AnomalyDetector(threshold=4).threshold, 4)
            self.assertEqual(AnomalyDetector(threshold=0).threshold, 0)


if __name__ == "__main__":
    unittest.main()
