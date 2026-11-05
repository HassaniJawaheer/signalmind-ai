from math import exp
import unittest

from config import pump
from data.simulation.dynamics import Dynamics
from data.simulation.state import PumpState


class CoolingTests(unittest.TestCase):
    def setUp(self):
        self.dynamics = Dynamics()
        self.nominal = self.dynamics.operating_point(pump.NOMINAL_SPEED_RPM, 1.0)

    def test_motor_temperature_matches_energy_balance(self):
        state = PumpState(rotational_speed=pump.NOMINAL_SPEED_RPM,
                          temperature=pump.AMBIENT_TEMPERATURE_C)
        duration = 100.0
        self.dynamics.update(state, pump.NOMINAL_SPEED_RPM, 1.0, 1.0, duration)
        losses = self.nominal['motor_loss_w']
        conductance = pump.MOTOR_THERMAL_CONDUCTANCE_W_K
        equilibrium = pump.AMBIENT_TEMPERATURE_C + losses / conductance
        expected = equilibrium + (pump.AMBIENT_TEMPERATURE_C - equilibrium) * exp(
            -conductance * duration / pump.MOTOR_HEAT_CAPACITY_J_K
        )
        self.assertAlmostEqual(state.temperature, expected)
        self.assertGreater(state.temperature, pump.AMBIENT_TEMPERATURE_C)
        self.assertLess(state.temperature, equilibrium)

    def test_ventilation_changes_only_thermal_behavior(self):
        healthy = PumpState(rotational_speed=pump.NOMINAL_SPEED_RPM, temperature=50.0)
        degraded = healthy.copy()
        self.dynamics.update(healthy, pump.NOMINAL_SPEED_RPM, 1.0, 1.0, 100.0)
        self.dynamics.update(degraded, pump.NOMINAL_SPEED_RPM, 1.0, 0.25, 100.0)
        self.assertGreater(degraded.temperature, healthy.temperature)
        for name in ('flow_rate', 'pressure', 'power_consumption', 'motor_loss_w'):
            self.assertEqual(getattr(healthy, name), getattr(degraded, name))

    def test_stopped_motor_cools_towards_ambient(self):
        state = PumpState(temperature=70.0)
        self.dynamics.update(state, 0.0, 1.0, 1.0, 100.0)
        self.assertLess(state.temperature, 70.0)
        self.assertGreater(state.temperature, pump.AMBIENT_TEMPERATURE_C)
        self.assertEqual(state.motor_loss_w, 0)
        self.assertEqual(state.power_consumption, 0)

    def test_thermal_integration_is_exact_for_constant_speed_and_controls(self):
        one_step = PumpState(rotational_speed=pump.NOMINAL_SPEED_RPM)
        many_steps = one_step.copy()
        self.dynamics.update(one_step, pump.NOMINAL_SPEED_RPM, 1.0, 0.5, 100)
        for _ in range(100):
            self.dynamics.update(many_steps, pump.NOMINAL_SPEED_RPM, 1.0, 0.5, 1)
        self.assertAlmostEqual(one_step.temperature, many_steps.temperature, places=9)


if __name__ == '__main__':
    unittest.main()
