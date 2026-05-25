from random import uniform

from data.simulation.state import MachineState


class SystemSensors:
    def __init__(self):
        self.bounds = {
            "vibration": (0.0, 1.0),
            "power_consumption": (0.0, 1.0),
            "machine_activity": (0.0, 1.0),
            "pressure": (0.0, 1.0),
            "flow_rate": (0.0, 1.0)
        }

        self.noise_amplitudes = {
            "temperature": 0.5,
            "vibration": 0.02,
            "power_consumption": 0.02,
            "machine_activity": 0.01,
            "pressure": 0.01,
            "flow_rate": 0.01
        }

    def _clamp(self, value, key):
        low, high = self.bounds[key]
        return max(low, min(value, high))

    def _noise(self, key):
        amplitude = self.noise_amplitudes[key]

        return uniform(
            -amplitude,
            amplitude
        )

    def _temperature(
        self,
        machine_state: MachineState
    ):
        return (
            machine_state.core_temperature
            + self._noise("temperature")
        )

    def _vibration(
        self,
        machine_state: MachineState
    ):
        vibration = (
            0.6 * machine_state.wear
            + 0.4 * machine_state.load
            + self._noise("vibration")
        )

        return self._clamp(
            vibration,
            "vibration"
        )

    def _power_consumption(
        self,
        machine_state: MachineState
    ):
        power = (
            0.7 * machine_state.load
            + 0.2 * machine_state.fan_speed
            + 0.1 * machine_state.flow_rate
            + self._noise("power_consumption")
        )

        return self._clamp(
            power,
            "power_consumption"
        )

    def _machine_activity(
        self,
        machine_state: MachineState
    ):
        activity = (
            machine_state.load
            + self._noise("machine_activity")
        )

        return self._clamp(
            activity,
            "machine_activity"
        )

    def _pressure(
        self,
        machine_state: MachineState
    ):
        pressure = (
            machine_state.pressure
            + self._noise("pressure")
        )

        return self._clamp(
            pressure,
            "pressure"
        )

    def _flow_rate(
        self,
        machine_state: MachineState
    ):
        flow = (
            machine_state.flow_rate
            + self._noise("flow_rate")
        )

        return self._clamp(
            flow,
            "flow_rate"
        )

    def generate(
        self,
        machine_state: MachineState
    ):
        return {
            "temperature": self._temperature(machine_state),
            "vibration": self._vibration(machine_state),
            "power_consumption": self._power_consumption(machine_state),
            "machine_activity": self._machine_activity(machine_state),
            "pressure": self._pressure(machine_state),
            "flow_rate": self._flow_rate(machine_state)
        }