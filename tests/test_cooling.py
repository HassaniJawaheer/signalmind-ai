import unittest
from unittest.mock import patch

from config import settings
from data.simulation.dynamics import Dynamics
from data.simulation.engine import Engine
from data.simulation.state import MachineState


class CoolingTests(unittest.TestCase):
    def test_combined_efficiency_drives_same_step_physics(self):
        with patch.object(settings, 'COOLING_WEAR_FACTOR', 0.10):
            dynamics = Dynamics()
        state = MachineState(initial_wear=1.0, initial_core_temperature=50.0)
        dynamics.update(state, scenario_efficiency=0.4)
        self.assertAlmostEqual(state.cooling_efficiency, 0.36)
        self.assertAlmostEqual(state.flow_rate, 0.36 * 0.5)
        self.assertAlmostEqual(state.pressure, 0.36 * 0.5 * 0.36)
        self.assertAlmostEqual(state.core_temperature, 50.0 - 3 * 0.36 * 0.5 * 0.36)

    def test_coefficient_and_wear_endpoints(self):
        for factor, wear, expected in (
            (0.10, 0.0, 0.7),
            (0.10, 0.5, 0.665),
            (0.10, 1.0, 0.63),
            (0.0, 1.0, 0.7),
            (0.20, 1.0, 0.56),
            (1.0, 1.0, 0.0),
        ):
            with self.subTest(factor=factor, wear=wear):
                with patch.object(settings, 'COOLING_WEAR_FACTOR', factor):
                    dynamics = Dynamics()
                state = MachineState(initial_wear=wear)
                dynamics.update(state, scenario_efficiency=0.7)
                self.assertAlmostEqual(state.cooling_efficiency, expected)

    def test_engine_recomputes_from_baseline_without_compounding(self):
        with patch.object(settings, 'COOLING_WEAR_FACTOR', 0.10):
            engine = Engine()
        engine.state.wear = 0.5
        with patch.object(engine.scenario, 'load', return_value=0.0):
            with patch.object(engine.scenario, 'cooling_efficiency', side_effect=[0.7, 0.4]):
                engine.step()
                self.assertAlmostEqual(engine.state.cooling_efficiency, 0.665)
                engine.step()
                self.assertAlmostEqual(engine.state.cooling_efficiency, 0.38)
        self.assertAlmostEqual(engine.internal_history[-1]['cooling_efficiency'], 0.38)

    def test_new_wear_affects_next_step(self):
        with patch.object(settings, 'COOLING_WEAR_FACTOR', 0.10):
            dynamics = Dynamics()
        state = MachineState(initial_load=1.0, initial_wear=0.5)
        dynamics.update(state, scenario_efficiency=1.0)
        self.assertAlmostEqual(state.cooling_efficiency, 0.95)
        self.assertGreater(state.wear, 0.5)
        previous_wear = state.wear
        dynamics.update(state, scenario_efficiency=1.0)
        self.assertAlmostEqual(state.cooling_efficiency, 1 - 0.10 * previous_wear)

    def test_invalid_coefficient(self):
        for factor in (-0.1, 1.1, float('nan'), float('inf')):
            with patch.object(settings, 'COOLING_WEAR_FACTOR', factor):
                with self.assertRaises(ValueError):
                    Dynamics()


if __name__ == '__main__':
    unittest.main()
