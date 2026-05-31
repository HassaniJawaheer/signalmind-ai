from math import sin, pi
from random import uniform


class Scenario:
    def __init__(self, day_length: int = 1000):
        self.day_length = day_length

    def load(self, t: int):
        x = t % self.day_length

        daily_cycle = 0.5 * (
            1 + sin(2 * pi * x / self.day_length - pi / 2)
        )

        peak_factor = uniform(0.8, 1.2)

        load = daily_cycle * peak_factor

        if uniform(0, 1) < 0.005:
            load += uniform(0.2, 0.4)

        return max(0, min(load, 1))

    def cooling_efficiency(self, t: int):
        base = 1 - 0.00002 * t

        if t > 3000:
            base -= 0.0001 * (t - 3000)

        return max(0.4, min(base, 1))