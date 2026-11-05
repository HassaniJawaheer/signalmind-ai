from random import Random
from config import pump, settings
from data.simulation.state import PumpState


class Sensors:
    def __init__(self, seed=None, noise=True):
        self.random = Random(seed)
        self.noise = noise

    def generate(self, state: PumpState, timestamp: str):
        measurements = {}
        for sensor in settings.SENSORS:
            value = getattr(state, sensor)
            if self.noise:
                amplitude = pump.SENSOR_NOISE_AMPLITUDES[sensor]
                value += self.random.uniform(-amplitude, amplitude)
            if sensor != "temperature":
                value = max(0.0, value)
            measurements[sensor] = value
        measurements["timestamp"] = timestamp
        return measurements
