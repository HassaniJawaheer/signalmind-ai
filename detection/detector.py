from config import settings
from detection.models import Detection
from detection.rules import RULES

class AnomalyDetector:


    def __init__(self, threshold=None):

        if threshold is None:
            threshold = settings.ANOMALY_SCORE_THRESHOLD

        self.threshold = threshold


    def detect(self, sensor_values:dict):
        score=0

        for rule in RULES:

            score += rule(

                sensor_values
            )

        trigger=score>=self.threshold

        return Detection(

            trigger=trigger,

            score=score,

            timestamp=sensor_values["timestamp"],

            sensor_values=sensor_values
        )
