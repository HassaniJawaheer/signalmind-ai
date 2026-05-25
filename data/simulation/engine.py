from data.simulation.state import MachineState
from data.simulation.dynamics import Dynamics
from data.simulation.sensors import Sensors
from data.scenarios.scenario import Scenario


class Engine:
    def __init__(
        self
    ):
        self.state = MachineState()

        self.dynamics = (
            Dynamics()
        )

        self.sensors = (
            Sensors()
        )

        self.scenario = (
            Scenario()
        )

        self.internal_history = []

    def run(
        self,
        n_steps: int
    ):

        history=[]

        self.internal_history=[]

        for t in range(
            n_steps
        ):

            self.state.load = (
                self.scenario.load(
                    t
                )
            )

            self.state.cooling_efficiency = (
                self.scenario.cooling_efficiency(
                    t
                )
            )

            self.state = (
                self.dynamics.update(
                    self.state
                )
            )

            self.internal_history.append(
                self.state.to_dict()
            )

            sensors = (
                self.sensors.generate(
                    self.state
                )
            )

            history.append(
                sensors
            )

        return history