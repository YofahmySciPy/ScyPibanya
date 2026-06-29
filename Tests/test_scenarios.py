import unittest

from src.scenarios import create_earth_moon, create_cannon_shot
from src import constants


class TestScenarios(unittest.TestCase):

    def test_earth_moon_returns_correct_structure(self):
        bodies, config = create_earth_moon()

        self.assertEqual(len(bodies), 2)
        self.assertIn("time_step", config)

    def test_earth_position_and_velocity(self):
        # earth should sit still at the origin (0, 0, 0)
        bodies, config = create_earth_moon()

        # bodies[0] is Earth, position[0] is x, position[1] is y
        self.assertAlmostEqual(bodies[0].position[0], 0)  # x
        self.assertAlmostEqual(bodies[0].position[1], 0)  # y

        # velocity[0] is vx, velocity[1] is vy
        self.assertAlmostEqual(bodies[0].velocity[0], 0)  # vx
        self.assertAlmostEqual(bodies[0].velocity[1], 0)  # vy

    def test_moon_position_and_velocity(self):
        # moon starts on the +x axis and moves in the +y direction
        bodies, config = create_earth_moon()

        # bodies[1] is the Moon
        self.assertAlmostEqual(bodies[1].position[0], constants.MOON_START_X)  # x = earth-moon distance
        self.assertEqual(bodies[1].position[1], 0)  # y = 0, moon starts on x axis

        self.assertEqual(bodies[1].velocity[0], 0)  # vx = 0, no movement in x
        self.assertAlmostEqual(bodies[1].velocity[1], constants.MOON_CIRCULAR_VELOCITY)  # vy = circular velocity

    def test_cannon_shot_returns_three_bodies(self):
        bodies, config = create_cannon_shot(7000, 0)

        self.assertEqual(len(bodies), 3)

    def test_cannon_shot_projectile_at_zero_degrees(self):
        # at 0 degrees the gun points straight at the moon (along +x axis)
        # cos(0) = 1, sin(0) = 0 -> projectile starts at (EARTH_RADIUS, 0, 0)
        bodies, config = create_cannon_shot(7000, 0)

        # bodies[2] is the projectile
        self.assertAlmostEqual(bodies[2].position[0], constants.EARTH_RADIUS)  # x = earth radius
        self.assertAlmostEqual(bodies[2].position[1], 0)  # y = 0


if __name__ == "__main__":
    unittest.main()
