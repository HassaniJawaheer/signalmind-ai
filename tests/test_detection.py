from data.scenarios.factory_machine import Factory
from detection.detector import AnomalyDetector
from detection.detection_history import DetectionHistory
from datetime import datetime


machine = Factory.create()

detector = AnomalyDetector()

history = DetectionHistory()


for _ in range(10000):

    sensors = machine.step()

    signal = detector.detect(
        sensor_values=sensors,
        timestamp=datetime.now()
    )

    history.save(signal)