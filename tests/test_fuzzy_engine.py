"""
test_fuzzy_engine.py
====================
Unit tests for the EV Charging Scheduler fuzzy-logic engine.

Run with:
    python -m pytest tests/ -v
"""

import unittest
import numpy as np
from fuzzy_engine import (
    get_optimal_charge,
    soc,
    price,
    time,
    charge_power,
    charging_ctrl,
)


class TestMembershipFunctions(unittest.TestCase):
    """Verify that membership functions are defined correctly."""

    def test_soc_terms_exist(self):
        """SOC must have Low, Medium, and High terms."""
        expected = {'Low', 'Medium', 'High'}
        self.assertEqual(set(soc.terms.keys()), expected)

    def test_price_terms_exist(self):
        """Price must have Low, Medium, and High terms."""
        expected = {'Low', 'Medium', 'High'}
        self.assertEqual(set(price.terms.keys()), expected)

    def test_time_terms_exist(self):
        """Time must have Short, Medium, and Long terms."""
        expected = {'Short', 'Medium', 'Long'}
        self.assertEqual(set(time.terms.keys()), expected)

    def test_charge_power_terms_exist(self):
        """Charge_Power must have Low, Medium, and High terms."""
        expected = {'Low', 'Medium', 'High'}
        self.assertEqual(set(charge_power.terms.keys()), expected)

    def test_soc_universe_range(self):
        """SOC universe should span 0 to 100."""
        self.assertEqual(soc.universe[0], 0)
        self.assertEqual(soc.universe[-1], 100)

    def test_price_universe_range(self):
        """Price universe should span 0 to 50."""
        self.assertEqual(price.universe[0], 0)
        self.assertEqual(price.universe[-1], 50)

    def test_time_universe_range(self):
        """Time universe should span 0 to 24."""
        self.assertEqual(time.universe[0], 0)
        self.assertEqual(time.universe[-1], 24)

    def test_charge_power_universe_range(self):
        """Charge_Power universe should span 0 to 22."""
        self.assertEqual(charge_power.universe[0], 0)
        self.assertEqual(charge_power.universe[-1], 22)

    def test_membership_values_bounded(self):
        """All membership function values must be in [0, 1]."""
        for var in [soc, price, time, charge_power]:
            for term_name in var.terms:
                mf_vals = var[term_name].mf
                self.assertTrue(np.all(mf_vals >= 0.0),
                                f"{var.label}.{term_name} has values < 0")
                self.assertTrue(np.all(mf_vals <= 1.0),
                                f"{var.label}.{term_name} has values > 1")


class TestFuzzyRules(unittest.TestCase):
    """Verify that the rule base is configured properly."""

    def test_rule_count(self):
        """The control system should contain exactly 20 rules."""
        self.assertEqual(len(list(charging_ctrl.rules)), 20)


class TestGetOptimalCharge(unittest.TestCase):
    """Integration tests for get_optimal_charge()."""

    def test_return_type(self):
        """get_optimal_charge should return a float."""
        result = get_optimal_charge(50, 25, 12)
        self.assertIsInstance(result, float)

    def test_output_within_range(self):
        """Output must be between 0 and 22 kW for any valid input."""
        test_cases = [
            (0, 0, 0),
            (50, 25, 12),
            (100, 50, 24),
            (10, 5, 2),
            (90, 45, 20),
        ]
        for soc_v, price_v, time_v in test_cases:
            with self.subTest(soc=soc_v, price=price_v, time=time_v):
                result = get_optimal_charge(soc_v, price_v, time_v)
                self.assertGreaterEqual(result, 0.0,
                                        f"Power below 0 for inputs ({soc_v}, {price_v}, {time_v})")
                self.assertLessEqual(result, 22.0,
                                     f"Power above 22 for inputs ({soc_v}, {price_v}, {time_v})")

    def test_low_soc_short_time_gives_high_power(self):
        """Low battery + leaving soon → must charge aggressively (>= 12 kW)."""
        result = get_optimal_charge(10, 10, 2)
        self.assertGreaterEqual(result, 12.0,
                                "Expected high power for low SOC + short departure time")

    def test_high_soc_high_price_gives_low_power(self):
        """Full battery + expensive electricity → minimal charging (<= 8 kW)."""
        result = get_optimal_charge(90, 45, 20)
        self.assertLessEqual(result, 8.0,
                             "Expected low power for high SOC + high price")

    def test_mid_soc_cheap_price_moderate_time(self):
        """Mid battery + cheap + moderate time → medium power (5-17 kW)."""
        result = get_optimal_charge(50, 10, 12)
        self.assertGreaterEqual(result, 5.0)
        self.assertLessEqual(result, 17.0)

    def test_low_soc_expensive_leaving_soon(self):
        """Low battery + expensive + leaving soon → still high (emergency)."""
        result = get_optimal_charge(15, 45, 2)
        self.assertGreaterEqual(result, 10.0,
                                "Emergency: must charge even if expensive")

    def test_deterministic_output(self):
        """Same inputs must always produce the same output."""
        r1 = get_optimal_charge(40, 20, 8)
        r2 = get_optimal_charge(40, 20, 8)
        self.assertAlmostEqual(r1, r2, places=5)

    def test_boundary_inputs(self):
        """Engine should handle boundary values without crashing."""
        boundary_cases = [
            (0, 0, 0),
            (100, 50, 24),
            (0, 50, 0),
            (100, 0, 24),
        ]
        for soc_v, price_v, time_v in boundary_cases:
            with self.subTest(soc=soc_v, price=price_v, time=time_v):
                result = get_optimal_charge(soc_v, price_v, time_v)
                self.assertIsInstance(result, float)


if __name__ == "__main__":
    unittest.main()
