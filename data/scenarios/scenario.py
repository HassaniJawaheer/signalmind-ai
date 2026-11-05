from math import isfinite, pi, sin
from config import pump


class Scenario:
    def __init__(self, mode=None):
        if mode is None:
            mode = pump.DEFAULT_SCENARIO
        if mode not in ("normal", "restriction", "ventilation_loss"):
            raise ValueError("Unknown pump scenario.")
        if not isfinite(pump.SPEED_CYCLE_SECONDS) or pump.SPEED_CYCLE_SECONDS <= 0:
            raise ValueError("SPEED_CYCLE_SECONDS must be positive.")
        if not isfinite(pump.FAULT_RAMP_SECONDS) or pump.FAULT_RAMP_SECONDS <= 0:
            raise ValueError("FAULT_RAMP_SECONDS must be positive.")
        self.mode = mode

    def controls(self, elapsed_seconds: float):
        speed_ratio = pump.SPEED_MEAN_RATIO + pump.SPEED_AMPLITUDE_RATIO * sin(
            2 * pi * elapsed_seconds / pump.SPEED_CYCLE_SECONDS
        )
        progress = (elapsed_seconds - pump.FAULT_START_SECONDS) / pump.FAULT_RAMP_SECONDS
        progress = max(0.0, min(progress, 1.0))
        resistance_factor = 1.0
        ventilation_factor = 1.0
        if self.mode == "restriction":
            resistance_factor += progress * (pump.RESTRICTED_RESISTANCE_FACTOR - 1)
        if self.mode == "ventilation_loss":
            ventilation_factor -= progress * (1 - pump.DEGRADED_VENTILATION_FACTOR)
        return {
            "speed_setpoint_rpm": pump.NOMINAL_SPEED_RPM * speed_ratio,
            "resistance_factor": resistance_factor,
            "ventilation_factor": ventilation_factor,
        }
