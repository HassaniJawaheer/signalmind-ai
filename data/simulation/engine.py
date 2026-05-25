from data.simulation.state import MachineState
from data.simulation.dynamics import SystemDynamics
from data.simulation.sensors import SystemSensors
from data.scenarios.scenario import Scenario


class Engine:
    def __init__(
        self
    ):
        self.state = MachineState()

        self.dynamics = (
            SystemDynamics()
        )

        self.sensors = (
            SystemSensors()
        )

        self.scenario = (
            Scenario()
        )

    def run(
        self,
        n_steps: int
    ):

        history=[]

        for t in range(
            n_steps
        ):

            self.state.load=(
                self.scenario.load(
                    t
                )
            )

            self.state.cooling_efficiency=(
                self.scenario.cooling_efficiency(
                    t
                )
            )

            self.state=(
                self.dynamics.update(
                    self.state
                )
            )

            sensors=(
                self.sensors.generate(
                    self.state
                )
            )

            history.append(
                sensors
            )

        return history