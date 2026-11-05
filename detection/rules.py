from config import pump, settings


def high_temperature(data):
    if data["temperature"] > settings.HIGH_TEMPERATURE_THRESHOLD:
        return settings.HIGH_TEMPERATURE_WEIGHT
    return 0


def low_flow_rate(data):
    speed = data["rotational_speed"]
    if speed < settings.MIN_MONITORED_SPEED_RPM:
        return 0
    expected_flow = pump.NOMINAL_FLOW_M3_H * speed / pump.NOMINAL_SPEED_RPM
    if data["flow_rate"] < expected_flow * settings.LOW_FLOW_RATIO_THRESHOLD:
        return settings.LOW_FLOW_RATE_WEIGHT
    return 0


def high_pressure(data):
    speed = data["rotational_speed"]
    if speed < settings.MIN_MONITORED_SPEED_RPM:
        return 0
    speed_ratio = speed / pump.NOMINAL_SPEED_RPM
    expected_pressure = (
        pump.WATER_DENSITY_KG_M3 * pump.GRAVITY_M_S2
        * pump.NOMINAL_HEAD_M * speed_ratio ** 2 / 100000
    )
    if data["pressure"] > expected_pressure * settings.HIGH_PRESSURE_RATIO_THRESHOLD:
        return settings.HIGH_PRESSURE_WEIGHT
    return 0


RULES = [high_temperature, low_flow_rate, high_pressure]
