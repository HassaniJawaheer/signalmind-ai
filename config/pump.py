# Illustrative water-loop pump, not a calibrated manufacturer model.
WATER_DENSITY_KG_M3 = 1000.0
GRAVITY_M_S2 = 9.81
NOMINAL_SPEED_RPM = 2900.0
NOMINAL_FLOW_M3_H = 12.0
NOMINAL_HEAD_M = 20.0
SHUTOFF_HEAD_M = 30.0

# Hydraulic conversion losses plus a separate nonzero shaft loss at shutoff.
HYDRAULIC_CONVERSION_EFFICIENCY = 0.75
PARASITIC_SHAFT_POWER_W = 100.0
MOTOR_EFFICIENCY = 0.88

AMBIENT_TEMPERATURE_C = 25.0
MOTOR_HEAT_CAPACITY_J_K = 4000.0
MOTOR_THERMAL_CONDUCTANCE_W_K = 4.0
SPEED_TIME_CONSTANT_SECONDS = 5.0
MAX_INTEGRATION_STEP_SECONDS = 0.25

DEFAULT_SCENARIO = "ventilation_loss"
SPEED_CYCLE_SECONDS = 1200.0
SPEED_MEAN_RATIO = 0.9
SPEED_AMPLITUDE_RATIO = 0.1
FAULT_START_SECONDS = 900.0
FAULT_RAMP_SECONDS = 600.0
RESTRICTED_RESISTANCE_FACTOR = 4.0
DEGRADED_VENTILATION_FACTOR = 0.25

SENSOR_NOISE_AMPLITUDES = {
    "temperature": 0.2,       # deg C
    "rotational_speed": 3.0,  # rpm
    "power_consumption": 0.005,  # kW
    "pressure": 0.005,        # bar differential
    "flow_rate": 0.02,        # m3/h
}
