from datetime import datetime, timedelta, timezone
from config import pump
from data.simulation.state import PumpState
from data.simulation.dynamics import Dynamics
from data.simulation.sensors import Sensors
from data.scenarios.scenario import Scenario


class Engine:
    def __init__(self, start_time: datetime | None = None,
                 step_duration: timedelta = timedelta(seconds=1),
                 scenario: Scenario | None = None, seed=None, noise=True):
        self.start_time = start_time if start_time is not None else datetime.now(timezone.utc)
        if self.start_time.tzinfo is None or self.start_time.utcoffset() is None:
            raise ValueError("start_time must include a timezone.")
        self.start_time = self.start_time.astimezone(timezone.utc)
        if step_duration <= timedelta(0):
            raise ValueError("step_duration must be positive.")
        self.step_duration = step_duration
        self.state = PumpState(temperature=pump.AMBIENT_TEMPERATURE_C)
        self.dynamics = Dynamics()
        self.sensors = Sensors(seed=seed, noise=noise)
        self.scenario = scenario if scenario is not None else Scenario()
        self.t = 0
        self.elapsed_seconds = 0.0
        self.internal_history = []

    def step(self):
        # The first sample is the initial state at t=0, before any integration.
        target_seconds = self.t * self.step_duration.total_seconds()
        while self.elapsed_seconds < target_seconds:
            duration = min(pump.MAX_INTEGRATION_STEP_SECONDS,
                           target_seconds - self.elapsed_seconds)
            midpoint_seconds = self.elapsed_seconds + duration / 2
            controls = self.scenario.controls(midpoint_seconds)
            self.dynamics.update(self.state, duration_seconds=duration, **controls)
            self.elapsed_seconds += duration
        snapshot = self.state.to_dict()
        snapshot["elapsed_seconds"] = self.elapsed_seconds
        self.internal_history.append(snapshot)
        timestamp = (self.start_time + self.t * self.step_duration).isoformat()
        sensors = self.sensors.generate(self.state, timestamp=timestamp)
        self.t += 1
        return sensors

    def run(self, n_steps: int):
        history = []
        self.internal_history = []
        for _ in range(n_steps):
            history.append(self.step())
        return history
