class MachineState:
    def __init__(
        self,
        initial_load: float = 0.0,
        initial_health: float = 1.0,
        initial_wear: float = 0.02,
        initial_core_temperature: float = 22.0,
        initial_cooling_efficiency: float = 1.0,
        initial_fan_speed: float = 0.0,
        initial_flow_rate: float = 0.0,
        initial_pressure: float = 0.0
    ):
        self.load = initial_load
        self.health = initial_health
        self.wear = initial_wear
        self.core_temperature = initial_core_temperature
        self.cooling_efficiency = initial_cooling_efficiency
        self.fan_speed = initial_fan_speed
        self.flow_rate = initial_flow_rate
        self.pressure = initial_pressure

    def to_dict(self):
        return {
            "load": self.load,
            "health": self.health,
            "wear": self.wear,
            "core_temperature": self.core_temperature,
            "cooling_efficiency": self.cooling_efficiency,
            "fan_speed": self.fan_speed,
            "flow_rate": self.flow_rate,
            "pressure": self.pressure
        }

    def copy(self):
        return MachineState(
            initial_load=self.load,
            initial_health=self.health,
            initial_wear=self.wear,
            initial_core_temperature=self.core_temperature,
            initial_cooling_efficiency=self.cooling_efficiency,
            initial_fan_speed=self.fan_speed,
            initial_flow_rate=self.flow_rate,
            initial_pressure=self.pressure
        )