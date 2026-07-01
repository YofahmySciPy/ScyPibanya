# tests for Analysis.py. The min_distance/sweep tests pin down the slow
# reference functions; TestSweepFast then checks the fast sweep the notebook
# uses, including that it agrees with the slow one. Speeds m/s, angles deg.

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

import constants
from analysis import sweep, sweep_fast, min_distance_to_moon
from scenarios import create_cannon_shot
from simulation import Simulation
from integrator import Verlet


# Known hit / miss cells (m/s, deg), checked against the sim.
HIT_SPEED, HIT_ANGLE = 12300.0, 10.0    # reaches the Moon (~1.74e6 m)
MISS_SPEED, MISS_ANGLE = 11000.0, 10.0  # too slow, stays ~2.3e8 m away

# "close enough to count as a hit". On a hit we sample ~1.74e6 m (the bodies
# merge a step before contact); nearest near-miss is ~1.98e6 m, so 1.8e6 splits
# them cleanly.
HIT_DISTANCE_THRESHOLD = 1.8e6


def _run(speed, angle, duration=3.5):
    bodies, config = create_cannon_shot(speed, angle)
    sim = Simulation(bodies, config, duration=duration, integrator=Verlet())
    sim.simulate()
    return sim.history


class TestMinDistanceToMoon(unittest.TestCase):
    # min_distance_to_moon() on single runs

    def test_hit_run_gets_within_one_moon_radius(self):
        history = _run(HIT_SPEED, HIT_ANGLE)
        md = min_distance_to_moon(history)
        # On a hit the projectile reaches the Moon's surface.
        self.assertLess(md, HIT_DISTANCE_THRESHOLD)
        # Sanity: it really is about the Moon's radius, not a tiny fluke.
        self.assertGreater(md, constants.MOON_RADIUS * 0.5)

    def test_miss_run_stays_far_away(self):
        history = _run(MISS_SPEED, MISS_ANGLE)
        md = min_distance_to_moon(history)
        # A clear miss stays orders of magnitude beyond the surface.
        self.assertGreater(md, 1.0e7)

    def test_returns_inf_without_projectile(self):
        # Earth-Moon only history has no "Projectile" body -> inf.
        bodies, config = create_cannon_shot(HIT_SPEED, HIT_ANGLE)
        sim = Simulation([b for b in bodies if b.name != "Projectile"],
                         config, duration=0.05, integrator=Verlet())
        sim.simulate()
        self.assertEqual(min_distance_to_moon(sim.history), float("inf"))


class TestSweepGrid(unittest.TestCase):
    # the slow sweep(): shape + known hit/miss cells

    @classmethod
    def setUpClass(cls):
        # run the sweep once, share it across the tests (each cell is a full sim)
        cls.speeds = [MISS_SPEED, HIT_SPEED]   # 11.0 and 12.3 km/s
        cls.angles = [HIT_ANGLE, 18.0]         # 10 and 18 deg
        cls.grid = sweep(cls.speeds, cls.angles)

    def test_grid_shape_and_keys(self):
        grid = self.grid
        self.assertEqual(set(grid), {"speeds", "angles", "hits", "min_dist"})
        self.assertEqual(grid["hits"].shape, (2, 2))
        self.assertEqual(grid["min_dist"].shape, (2, 2))

    def test_known_hit_cell_is_hit(self):
        grid = self.grid
        i = list(self.speeds).index(HIT_SPEED)
        j = list(self.angles).index(HIT_ANGLE)
        self.assertTrue(grid["hits"][i, j])
        self.assertLess(grid["min_dist"][i, j], HIT_DISTANCE_THRESHOLD)

    def test_known_miss_cell_is_miss(self):
        grid = self.grid
        i = list(self.speeds).index(MISS_SPEED)
        j = list(self.angles).index(HIT_ANGLE)
        self.assertFalse(grid["hits"][i, j])
        self.assertGreater(grid["min_dist"][i, j], 1.0e7)


class TestSweepFast(unittest.TestCase):
    # the fast sweep the notebook uses, plus it must agree with the slow one

    def test_known_hit_and_miss_cells(self):
        grid = sweep_fast([MISS_SPEED, HIT_SPEED], [HIT_ANGLE])
        # rows = speeds, cols = angles
        self.assertFalse(grid["hits"][0, 0])   # 11.0 km/s @ 10 deg -> miss
        self.assertTrue(grid["hits"][1, 0])    # 12.3 km/s @ 10 deg -> hit
        self.assertGreater(grid["min_dist"][0, 0], 1.0e7)
        self.assertLess(grid["min_dist"][1, 0], HIT_DISTANCE_THRESHOLD)

    def test_grid_shape_and_keys(self):
        grid = sweep_fast([11.7e3, 12.3e3, 13.0e3], [8, 10, 12, 14])
        self.assertEqual(set(grid), {"speeds", "angles", "hits", "min_dist"})
        self.assertEqual(grid["hits"].shape, (3, 4))
        self.assertEqual(grid["min_dist"].shape, (3, 4))

    def test_agrees_with_reference_sweep(self):
        # Same hit/miss classification as the trusted (slow) sweep.
        speeds = [11.7e3, 12.3e3, 13.0e3]
        angles = [8.0, 12.0]
        ref = sweep(speeds, angles)
        fast = sweep_fast(speeds, angles)
        np.testing.assert_array_equal(fast["hits"], ref["hits"])


if __name__ == "__main__":
    unittest.main()