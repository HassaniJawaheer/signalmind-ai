from math import exp, isfinite, sqrt
from config import pump
from data.simulation.state import PumpState


class Dynamics:
    def __init__(self):
        positive_parameters = (
            pump.WATER_DENSITY_KG_M3, pump.GRAVITY_M_S2,
            pump.NOMINAL_SPEED_RPM, pump.NOMINAL_FLOW_M3_H,
            pump.NOMINAL_HEAD_M, pump.SHUTOFF_HEAD_M,
            pump.MOTOR_HEAT_CAPACITY_J_K, pump.MOTOR_THERMAL_CONDUCTANCE_W_K,
            pump.SPEED_TIME_CONSTANT_SECONDS, pump.MAX_INTEGRATION_STEP_SECONDS,
        )
        if any(not isfinite(value) or value <= 0 for value in positive_parameters):
            raise ValueError("Pump and integration parameters must be finite and positive.")
        if pump.SHUTOFF_HEAD_M <= pump.NOMINAL_HEAD_M:
            raise ValueError("Shutoff head must exceed nominal operating head.")
        for efficiency in (pump.HYDRAULIC_CONVERSION_EFFICIENCY, pump.MOTOR_EFFICIENCY):
            if not 0 < efficiency <= 1:
                raise ValueError("Efficiencies must be in (0, 1].")
        if not isfinite(pump.PARASITIC_SHAFT_POWER_W) or pump.PARASITIC_SHAFT_POWER_W < 0:
            raise ValueError("Parasitic shaft power must be finite and non-negative.")
        if not isfinite(pump.AMBIENT_TEMPERATURE_C):
            raise ValueError("Ambient temperature must be finite.")
        self.pump_curve_coefficient = (
            (pump.SHUTOFF_HEAD_M - pump.NOMINAL_HEAD_M) / pump.NOMINAL_FLOW_M3_H ** 2
        )
        self.circuit_coefficient = pump.NOMINAL_HEAD_M / pump.NOMINAL_FLOW_M3_H ** 2

    def operating_point(self, speed_rpm: float, resistance_factor: float):
        if not isfinite(speed_rpm) or not 0 <= speed_rpm <= pump.NOMINAL_SPEED_RPM:
            raise ValueError("Speed must be between zero and nominal speed.")
        if not isfinite(resistance_factor) or resistance_factor <= 0:
            raise ValueError("Circuit resistance factor must be positive.")
        ratio = speed_rpm / pump.NOMINAL_SPEED_RPM
        resistance = self.circuit_coefficient * resistance_factor
        # H_pump = H_shutoff*r^2 - A*Q^2; H_circuit = R*Q^2, no static lift.
        flow_m3_h = sqrt(pump.SHUTOFF_HEAD_M * ratio ** 2 / (
            self.pump_curve_coefficient + resistance
        ))
        head_m = resistance * flow_m3_h ** 2
        pressure_pa = pump.WATER_DENSITY_KG_M3 * pump.GRAVITY_M_S2 * head_m
        hydraulic_power_w = pressure_pa * flow_m3_h / 3600
        shaft_power_w = (
            hydraulic_power_w / pump.HYDRAULIC_CONVERSION_EFFICIENCY
            + pump.PARASITIC_SHAFT_POWER_W * ratio ** 3
        )
        electrical_power_w = shaft_power_w / pump.MOTOR_EFFICIENCY
        return {
            "flow_rate": flow_m3_h,
            "pressure": pressure_pa / 100000,
            "power_consumption": electrical_power_w / 1000,
            "hydraulic_power_w": hydraulic_power_w,
            "shaft_power_w": shaft_power_w,
            "motor_loss_w": electrical_power_w - shaft_power_w,
        }

    def update(self, state: PumpState, speed_setpoint_rpm: float,
               resistance_factor: float, ventilation_factor: float,
               duration_seconds: float):
        if not isfinite(duration_seconds) or duration_seconds <= 0:
            raise ValueError("Integration duration must be positive.")
        if not isfinite(speed_setpoint_rpm) or not 0 <= speed_setpoint_rpm <= pump.NOMINAL_SPEED_RPM:
            raise ValueError("Speed setpoint must be between zero and nominal speed.")
        if not isfinite(ventilation_factor) or not 0 < ventilation_factor <= 1:
            raise ValueError("Ventilation factor must be in (0, 1].")
        # First-order speed response; torque/inertia and hydraulic transients are omitted.
        decay = exp(-duration_seconds / pump.SPEED_TIME_CONSTANT_SECONDS)
        midpoint_speed = speed_setpoint_rpm + (state.rotational_speed - speed_setpoint_rpm) * sqrt(decay)
        new_speed = speed_setpoint_rpm + (state.rotational_speed - speed_setpoint_rpm) * decay
        midpoint = self.operating_point(midpoint_speed, resistance_factor)
        point = self.operating_point(new_speed, resistance_factor)

        # Only motor losses heat this thermal mass; pump losses go elsewhere.
        conductance = pump.MOTOR_THERMAL_CONDUCTANCE_W_K * ventilation_factor
        equilibrium = pump.AMBIENT_TEMPERATURE_C + midpoint["motor_loss_w"] / conductance
        thermal_decay = exp(-conductance * duration_seconds / pump.MOTOR_HEAT_CAPACITY_J_K)
        state.temperature = equilibrium + (state.temperature - equilibrium) * thermal_decay
        state.rotational_speed = new_speed
        state.resistance_factor = resistance_factor
        state.ventilation_factor = ventilation_factor
        for name, value in point.items():
            setattr(state, name, value)
        return state
