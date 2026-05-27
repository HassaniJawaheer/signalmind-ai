from detection.rules import RULES


class RuleScorer:

    def compute(self,data):

        score=0
        reasons=[]

        for rule in RULES:

            triggered,weight,reason=rule(data)

            if triggered:

                score+=weight
                reasons.append(reason)

        return score,reasons