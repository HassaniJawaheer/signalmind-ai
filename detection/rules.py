def high_temperature(data):

    temp=data["temperature"]

    if temp>85:
        return True,2,"high_temperature"

    return False,0,None


def high_vibration(data):

    if data["vibration"]>0.8:
        return True,2,"high_vibration"

    return False,0,None


def low_pressure(data):

    if data["pressure"]<0.25:
        return True,2,"low_pressure"

    return False,0,None


def low_flow(data):

    if data["flow_rate"]<0.25:
        return True,1,"low_flow"

    return False,0,None


def cooling_failure_combo(data):

    if (
        data["temperature"]>85
        and data["pressure"]<0.25
        and data["flow_rate"]<0.25
    ):

        return True,3,"cooling_failure_pattern"

    return False,0,None


RULES=[

    high_temperature,
    high_vibration,
    low_pressure,
    low_flow,
    cooling_failure_combo
]