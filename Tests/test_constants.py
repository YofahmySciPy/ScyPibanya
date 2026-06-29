import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import constants as C


class TestConstants(unittest.TestCase):

    def test_basic_values_are_positive(self):
        for value in (C.G, C.EARTH_MASS, C.EARTH_RADIUS,
                      C.MOON_MASS, C.MOON_RADIUS, C.EARTH_MOON_DISTANCE):
            self.assertGreater(value, 0.0)

    def test_time_units(self):
        self.assertEqual(C.MINUTE, 60.0)
        self.assertEqual(C.HOUR, 3600.0)
        self.assertEqual(C.DAY, 86400.0)

    def test_kilometer_unit(self):
        self.assertEqual(C.KM, 1000.0)

    def test_escape_velocity_is_about_11200_ms(self):
        self.assertAlmostEqual(C.EARTH_ESCAPE_VELOCITY, 11186.0, delta=50.0)

    def test_moon_circular_velocity_matches_measured_speed(self):
        self.assertAlmostEqual(C.MOON_CIRCULAR_VELOCITY, C.MOON_ORBITAL_SPEED,
                               delta=15.0)

    def test_moon_start_state(self):
        self.assertEqual(C.MOON_START_X, C.EARTH_MOON_DISTANCE)
        self.assertEqual(C.MOON_START_VY, C.MOON_ORBITAL_SPEED)

    def test_cannon_speeds(self):
        self.assertEqual(C.CANNON_SPEEDS, (7000.0, 9000.0, 12000.0))

    def test_cannon_lead_angles(self):
        self.assertEqual(C.CANNON_LEAD_ANGLES, (0.0, 15.0, 30.0))


if __name__ == "__main__":
    unittest.main()
