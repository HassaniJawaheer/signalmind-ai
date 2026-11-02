from datetime import datetime, timedelta, timezone

from data.simulation.state import MachineState
from data.simulation.dynamics import Dynamics
from data.simulation.sensors import Sensors
from data.scenarios.scenario import Scenario


class Engine:
    def __init__(self, start_time: datetime | None = None,
                 step_duration: timedelta = timedelta(seconds=1)):
        self.start_time = start_time if start_time is not None else datetime.now(timezone.utc)
        if self.start_time.tzinfo is None or self.start_time.utcoffset() is None:
            raise ValueError("start_time must include a timezone.")
        self.start_time = self.start_time.astimezone(timezone.utc)
        if step_duration <= timedelta(0):
            raise ValueError("step_duration must be positive.")
        self.step_duration = step_duration
        self.state = MachineState()

        self.dynamics = Dynamics()
        self.sensors = Sensors()
        self.scenario = Scenario()

        self.t = 0
        self.internal_history = []

    def step(self):
        self.state.load = self.scenario.load(
            self.t
        )

        scenario_efficiency = self.scenario.cooling_efficiency(self.t)

        self.state = self.dynamics.update(
            self.state,
            scenario_efficiency
        )

        self.internal_history.append(
            self.state.to_dict()
        )

        sensors = self.sensors.generate(
            self.state,
            timestamp=(self.start_time + self.t * self.step_duration).isoformat()
        )

        self.t += 1

        return sensors

    def run(
        self,
        n_steps: int
    ):
        history = []

        self.internal_history = []

        for _ in range(n_steps):
            history.append(
                self.step()
            )

        return history
