from dataclasses import asdict, dataclass, replace


@dataclass
class PumpState:
    rotational_speed: float = 0.0  # rpm
    temperature: float = 25.0      # motor casing, deg C
    flow_rate: float = 0.0         # m3/h
    pressure: float = 0.0          # bar, discharge minus suction
    power_consumption: float = 0.0 # kW, electrical input
    hydraulic_power_w: float = 0.0
    shaft_power_w: float = 0.0
    motor_loss_w: float = 0.0
    resistance_factor: float = 1.0
    ventilation_factor: float = 1.0

    def to_dict(self):
        return asdict(self)

    def copy(self):
        return replace(self)
