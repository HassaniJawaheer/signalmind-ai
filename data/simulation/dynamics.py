from data.simulation.state import MachineState


class SystemDynamics:
    def __init__(self):
        self.bounds = {
            "load": (0.0, 1.0),
            "health": (0.0, 1.0),
            "wear": (0.0, 1.0),
            "core_temperature": (20.0, 120.0),
            "cooling_efficiency": (0.0, 1.0),
            "fan_speed": (0.0, 1.0),
            "flow_rate": (0.0, 1.0),
            "pressure": (0.0, 1.0)
        }

    def _clamp(self, value, key):
        low, high = self.bounds[key]
        return max(low, min(value, high))

    def _update_load(
        self,
        machine_state: MachineState,
        new_load: float
    ):
        machine_state.load = self._clamp(
            new_load,
            "load"
        )

        return machine_state

    def _update_health(
        self,
        machine_state: MachineState,
        health_wear_factor: float = 0.001,
        health_temp_factor: float = 0.0005
    ):
        machine_state.health -= (
            health_wear_factor *
            machine_state.wear
        )

        machine_state.health -= (
            health_temp_factor *
            max(
                0,
                machine_state.core_temperature - 70
            )
        )

        machine_state.health = self._clamp(
            machine_state.health,
            "health"
        )

        return machine_state

    def _update_wear(
        self,
        machine_state: MachineState,
        wear_load_factor: float = 0.001,
        wear_temp_factor: float = 0.001
    ):
        machine_state.wear += (
            wear_load_factor *
            machine_state.load
        )

        machine_state.wear += (
            wear_temp_factor *
            max(
                0,
                machine_state.core_temperature - 70
            )
        )

        machine_state.wear = self._clamp(
            machine_state.wear,
            "wear"
        )

        return machine_state

    def _update_core_temperature(
        self,
        machine_state: MachineState,
        heating_factor: float = 5.0,
        cooling_factor: float = 3.0
    ):
        cooling = (
            machine_state.flow_rate *
            machine_state.cooling_efficiency
)

        machine_state.core_temperature += (
            heating_factor *
            machine_state.load
        )

        machine_state.core_temperature -= (
            cooling_factor *
            cooling
        )

        machine_state.core_temperature = self._clamp(
            machine_state.core_temperature,
            "core_temperature"
        )

        return machine_state

    def _update_fan_speed(
        self,
        machine_state: MachineState
    ):
        machine_state.fan_speed = (
            machine_state.core_temperature / 100
        )

        machine_state.fan_speed = self._clamp(
            machine_state.fan_speed,
            "fan_speed"
        )

        return machine_state

    def _update_flow_rate(
        self,
        machine_state: MachineState
    ):
        machine_state.flow_rate = (
            machine_state.cooling_efficiency *
            machine_state.fan_speed
        )

        machine_state.flow_rate = self._clamp(
            machine_state.flow_rate,
            "flow_rate"
        )

        return machine_state

    def _update_pressure(
        self,
        machine_state: MachineState
    ):
        machine_state.pressure = (
            machine_state.flow_rate *
            machine_state.cooling_efficiency
        )

        machine_state.pressure = self._clamp(
            machine_state.pressure,
            "pressure"
        )

        return machine_state

    def _update_cooling_efficiency(
        self,
        machine_state: MachineState,
        wear_factor: float = 0.0005
    ):
        machine_state.cooling_efficiency -= (
            wear_factor *
            machine_state.wear
        )

        machine_state.cooling_efficiency = self._clamp(
            machine_state.cooling_efficiency,
            "cooling_efficiency"
        )

        return machine_state


