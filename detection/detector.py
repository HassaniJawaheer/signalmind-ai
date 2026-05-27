from detection.scorer import RuleScorer
from detection.models import DetectionResult


class AnomalyDetector:

    def __init__(
        self,
        threshold:int=5
    ):

        self.threshold=threshold
        self.scorer=RuleScorer()


    def detect(self,data):

        score,reasons=self.scorer.compute(data)

        return DetectionResult(

            anomaly=score>=self.threshold,
            score=score,
            reasons=reasons
        )