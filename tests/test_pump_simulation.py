from datetime import datetime, timedelta, timezone
from math import sqrt
import unittest
from unittest.mock import patch

from config import pump, settings
from data.scenarios.scenario import Scenario
from data.simulation.dynamics import Dynamics
from data.simulation.engine import Engine
from data.simulation.state import PumpState
from detection.detector import AnomalyDetector
from investigation.prompts.pump_description import describe_pump


class PumpSimulationTests(unittest.TestCase):
    def test_nominal_point_and_power_balance(self):
        point = Dynamics().operating_point(2900, 1)
        self.assertAlmostEqual(point['flow_rate'], 12)
        self.assertAlmostEqual(point['pressure'], 1.962)
        self.assertAlmostEqual(point['hydraulic_power_w'], 654)
        self.assertAlmostEqual(point['shaft_power_w'], 972)
        self.assertAlmostEqual(point['power_consumption'], 972 / 0.88 / 1000)
        self.assertAlmostEqual(point['motor_loss_w'], point['power_consumption'] * 1000 - 972)
        self.assertGreater(point['shaft_power_w'], point['hydraulic_power_w'])
        self.assertGreater(point['motor_loss_w'], 0)

    def test_restriction_reduces_flow_and_raises_differential_pressure(self):
        dynamics = Dynamics()
        nominal = dynamics.operating_point(2900, 1)
        restricted = dynamics.operating_point(2900, 4)
        self.assertAlmostEqual(restricted['flow_rate'], 12 / sqrt(3))
        self.assertGreater(restricted['pressure'], nominal['pressure'])
        self.assertLess(restricted['flow_rate'], nominal['flow_rate'])
        self.assertLess(restricted['power_consumption'], nominal['power_consumption'])

    def test_speed_affinity_and_nonzero_shutoff_power_limit(self):
        dynamics = Dynamics()
        full = dynamics.operating_point(2900, 1)
        half = dynamics.operating_point(1450, 1)
        self.assertAlmostEqual(half['flow_rate'] / full['flow_rate'], 0.5)
        self.assertAlmostEqual(half['pressure'] / full['pressure'], 0.25)
        self.assertAlmostEqual(half['power_consumption'] / full['power_consumption'], 0.125)
        near_closed = dynamics.operating_point(2900, 1e12)
        self.assertGreaterEqual(near_closed['shaft_power_w'], pump.PARASITIC_SHAFT_POWER_W)

    def test_timestamp_matches_initial_state_and_elapsed_physics(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        engine = Engine(start_time=start, step_duration=timedelta(seconds=5), noise=False)
        first = engine.step()
        self.assertEqual(first['timestamp'], start.isoformat())
        self.assertEqual(first['rotational_speed'], 0)
        second = engine.step()
        self.assertEqual(second['timestamp'], (start + timedelta(seconds=5)).isoformat())
        self.assertEqual(engine.elapsed_seconds, 5)
        self.assertGreater(second['rotational_speed'], 0)
        self.assertLess(second['rotational_speed'], pump.NOMINAL_SPEED_RPM)
        self.assertEqual(set(second), set(settings.SENSORS) | {'timestamp'})
        self.assertEqual(len(settings.SENSORS), 5)

    def test_output_step_does_not_change_physics_at_same_elapsed_time(self):
        states = []
        for sample_seconds in (0.5, 1, 5):
            engine = Engine(step_duration=timedelta(seconds=sample_seconds),
                            scenario=Scenario('restriction'), noise=False)
            engine.run(int(1800 / sample_seconds) + 1)
            states.append(engine.state.to_dict())
        for state in states[1:]:
            for key, value in states[0].items():
                self.assertAlmostEqual(state[key], value, places=8, msg=key)

    def test_seed_makes_measurements_reproducible(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(Engine(start_time=start, seed=42).run(20),
                         Engine(start_time=start, seed=42).run(20))

    def test_scenarios_are_defined_in_seconds(self):
        before = pump.FAULT_START_SECONDS - 1
        after = pump.FAULT_START_SECONDS + pump.FAULT_RAMP_SECONDS
        for mode in ('normal', 'restriction', 'ventilation_loss'):
            scenario = Scenario(mode)
            self.assertEqual(scenario.controls(before)['resistance_factor'], 1)
            self.assertEqual(scenario.controls(before)['ventilation_factor'], 1)
        self.assertEqual(Scenario('restriction').controls(after)['resistance_factor'], 4)
        self.assertEqual(Scenario('ventilation_loss').controls(after)['ventilation_factor'], 0.25)
        self.assertEqual(Scenario('normal').controls(after)['ventilation_factor'], 1)

    def test_normal_operation_and_both_faults_with_real_detector(self):
        detector = AnomalyDetector()
        for mode in ('normal', 'restriction', 'ventilation_loss'):
            engine = Engine(scenario=Scenario(mode), seed=42)
            first_alert = None
            for _ in range(6001):
                measurement = engine.step()
                if detector.detect(measurement).trigger:
                    first_alert = engine.elapsed_seconds
                    break
            if mode == 'normal':
                self.assertIsNone(first_alert)
                self.assertLess(engine.state.temperature, settings.HIGH_TEMPERATURE_THRESHOLD)
            else:
                self.assertIsNotNone(first_alert, mode)
                self.assertGreater(first_alert, pump.FAULT_START_SECONDS)

    def test_invalid_controls_and_parameters(self):
        dynamics = Dynamics()
        for speed, resistance in ((-1, 1), (3000, 1), (1000, 0), (1000, float('nan'))):
            with self.assertRaises(ValueError):
                dynamics.operating_point(speed, resistance)
        with self.assertRaises(ValueError):
            dynamics.update(PumpState(), 1000, 1, 0, 1)
        with patch.object(pump, 'MOTOR_EFFICIENCY', 0):
            with self.assertRaises(ValueError):
                Dynamics()
        with self.assertRaises(ValueError):
            Scenario('unknown')

    def test_description_has_units_but_no_hidden_fault_state(self):
        text = describe_pump()
        for sensor in settings.SENSORS:
            self.assertIn(sensor, text)
        for unit in ('rpm', 'm3/h', 'bar', 'kW', 'deg C'):
            self.assertIn(unit, text)
        for secret in ('FAULT_START_SECONDS', 'ventilation_loss', 'resistance_factor'):
            self.assertNotIn(secret, text)


if __name__ == '__main__':
    unittest.main()
