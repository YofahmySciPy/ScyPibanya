import os
import sys
import unittest

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from body import Body


class TestBody(unittest.TestCase):

    def setUp(self):
        # Runs automatically before every test, so each test starts
        # from the same fresh body.
        self.body = Body("Test", mass=10.0, radius=2.0,
                         position=[0.0, 0.0, 0.0],
                         velocity=[1.0, 2.0, 3.0])

    def test_attributes_are_stored(self):
        b = self.body
        self.assertEqual(b.name, "Test")
        self.assertEqual(b.mass, 10.0)
        self.assertEqual(b.radius, 2.0)
        self.assertTrue(np.allclose(b.position, [0.0, 0.0, 0.0]))
        self.assertTrue(np.allclose(b.velocity, [1.0, 2.0, 3.0]))

    def test_position_previous_is_not_set_yet(self):
        self.assertIsNone(self.body.position_previous)

    def test_acceleration_starts_at_zero(self):
        self.assertTrue(np.allclose(self.body.acceleration, [0.0, 0.0, 0.0]))

    def test_diameter_is_twice_the_radius(self):
        self.assertEqual(self.body.diameter(), 4.0)

    def test_distance_to_uses_pythagoras(self):
        a = Body("A", 1.0, 1.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        b = Body("B", 1.0, 1.0, [3.0, 4.0, 0.0], [0.0, 0.0, 0.0])
        self.assertAlmostEqual(a.distance_to(b), 5.0)

    def test_distance_vector_to_points_from_self_to_other(self):
        a = Body("A", 1.0, 1.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        b = Body("B", 1.0, 1.0, [3.0, 4.0, 0.0], [0.0, 0.0, 0.0])
        self.assertTrue(np.allclose(a.distance_vector_to(b), [3.0, 4.0, 0.0]))
        self.assertTrue(np.allclose(b.distance_vector_to(a), [-3.0, -4.0, 0.0]))

    def test_is_touching_true_when_spheres_overlap(self):
        a = Body("A", 1.0, 2.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        b = Body("B", 1.0, 2.0, [3.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        self.assertTrue(a.is_touching(b))

    def test_is_touching_false_when_far_apart(self):
        a = Body("A", 1.0, 1.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        b = Body("B", 1.0, 1.0, [10.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        self.assertFalse(a.is_touching(b))

    def test_momentum_is_mass_times_velocity(self):
        self.assertTrue(np.allclose(self.body.momentum(), [10.0, 20.0, 30.0]))

    def test_negative_mass_raises(self):
        with self.assertRaises(ValueError):
            Body("Bad", -1.0, 1.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

    def test_zero_radius_raises(self):
        with self.assertRaises(ValueError):
            Body("Bad", 1.0, 0.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

    def test_wrong_position_length_raises(self):
        with self.assertRaises(ValueError):
            Body("Bad", 1.0, 1.0, [0.0, 0.0], [0.0, 0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
