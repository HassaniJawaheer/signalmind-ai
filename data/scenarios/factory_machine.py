from datetime import datetime, timedelta
from data.scenarios.scenario import Scenario
from data.simulation.engine import Engine


class Factory:
    @staticmethod
    def create(start_time: datetime | None = None,
               step_duration: timedelta = timedelta(seconds=1),
               scenario: Scenario | None = None, seed=None, noise=True):
        return Engine(start_time=start_time, step_duration=step_duration,
                      scenario=scenario, seed=seed, noise=noise)
