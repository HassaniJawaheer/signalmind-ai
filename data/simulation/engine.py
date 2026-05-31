from data.simulation.state import MachineState
from data.simulation.dynamics import Dynamics
from data.simulation.sensors import Sensors
from data.scenarios.scenario import Scenario


class Engine:
    def __init__(self):
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

        self.state.cooling_efficiency = (
            self.scenario.cooling_efficiency(
                self.t
            )
        )

        self.state = self.dynamics.update(
            self.state
        )

        self.internal_history.append(
            self.state.to_dict()
        )

        sensors = self.sensors.generate(
            self.state
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