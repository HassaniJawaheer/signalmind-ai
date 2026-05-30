from config.settings import (
    HIGH_TEMPERATURE_THRESHOLD,
    HIGH_VIBRATION_THRESHOLD,
    LOW_PRESSURE_THRESHOLD,
    LOW_FLOW_RATE_THRESHOLD,
    HIGH_TEMPERATURE_WEIGHT,
    HIGH_VIBRATION_WEIGHT,
    LOW_PRESSURE_WEIGHT,
    LOW_FLOW_RATE_WEIGHT,
    COOLING_COMBINATION_WEIGHT
)


def high_temperature(data):

    if data["temperature"] > HIGH_TEMPERATURE_THRESHOLD:

        return HIGH_TEMPERATURE_WEIGHT

    return 0


def high_vibration(data):

    if data["vibration"] > HIGH_VIBRATION_THRESHOLD:

        return HIGH_VIBRATION_WEIGHT

    return 0


def low_pressure(data):

    if data["pressure"] < LOW_PRESSURE_THRESHOLD:

        return LOW_PRESSURE_WEIGHT

    return 0


def low_flow_rate(data):

    if data["flow_rate"] < LOW_FLOW_RATE_THRESHOLD:

        return LOW_FLOW_RATE_WEIGHT

    return 0


def cooling_combination(data):

    if (
        data["temperature"] > HIGH_TEMPERATURE_THRESHOLD
        and data["pressure"] < LOW_PRESSURE_THRESHOLD
        and data["flow_rate"] < LOW_FLOW_RATE_THRESHOLD
    ):

        return COOLING_COMBINATION_WEIGHT

    return 0


RULES = [

    high_temperature,

    high_vibration,

    low_pressure,

    low_flow_rate,

    cooling_combination
]