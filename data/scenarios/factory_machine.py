from datetime import datetime, timedelta
from data.simulation.engine import Engine


class Factory:
    @staticmethod
    def create(start_time: datetime | None = None,
               step_duration: timedelta = timedelta(seconds=1)):
        return Engine(start_time=start_time, step_duration=step_duration)
