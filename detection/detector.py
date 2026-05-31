from detection.models import Detection
from detection.rules import RULES
import datetime

class AnomalyDetector:


    def __init__(self, threshold=5):

        self.threshold=threshold


    def detect(self, sensor_values:dict, timestamp:datetime.datetime):
        score=0

        for rule in RULES:

            score += rule(

                sensor_values
            )

        trigger=score>=self.threshold

        return Detection(

            trigger=trigger,

            score=score,

            timestamp=timestamp,

            sensor_values=sensor_values
        )