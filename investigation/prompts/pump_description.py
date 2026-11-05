from config import pump, settings


def describe_pump() -> str:
    nominal_pressure = pump.WATER_DENSITY_KG_M3 * pump.GRAVITY_M_S2 * pump.NOMINAL_HEAD_M / 100000
    return (
        "Equipment: simplified variable-speed centrifugal water pump in a closed loop, "
        "no static lift; air-cooled motor. Parameters are illustrative, not calibrated.\n"
        f"rotational_speed: measured rpm, commanded range 0-{pump.NOMINAL_SPEED_RPM:g}; "
        "speed changes can be normal operation.\n"
        f"flow_rate: m3/h, nominal {pump.NOMINAL_FLOW_M3_H:g} at nominal speed; "
        "healthy-circuit flow scales approximately with speed.\n"
        f"pressure: discharge-minus-suction pressure in bar, nominal {nominal_pressure:.3f}; "
        "healthy-circuit pressure scales approximately with speed squared. "
        "Restriction can reduce flow while increasing pressure at the same speed.\n"
        "power_consumption: electrical input in kW, depends on hydraulic work and losses; "
        "it need not increase when flow is restricted.\n"
        f"temperature: motor casing in deg C, ambient {pump.AMBIENT_TEMPERATURE_C:g}; "
        "responds slowly to motor losses and ventilation. It is not water temperature.\n"
        f"Demonstration alert criteria: temperature > {settings.HIGH_TEMPERATURE_THRESHOLD:g} deg C; "
        f"above {settings.MIN_MONITORED_SPEED_RPM:g} rpm, flow below "
        f"{settings.LOW_FLOW_RATIO_THRESHOLD:g} times its healthy reference or pressure above "
        f"{settings.HIGH_PRESSURE_RATIO_THRESHOLD:g} times its healthy reference. "
        "These are investigation thresholds, not safety standards. "
        "Sensor noise is present; a stable value is not necessarily healthy. "
        "No vibration sensor is available; specific bearing faults cannot be established.\n"
    )
