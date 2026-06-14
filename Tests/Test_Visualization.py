import os
import sys
import unittest

import matplotlib
matplotlib.use("Agg")  # headless backend - no display needed for the tests
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from Simulation import Simulation
from Scenarios import create_earth_moon, create_cannon_shot
import Constants
import Visualization


class Test_ExtractTrajectories(unittest.TestCase):

    def setUp(self):
        bodies, config = create_earth_moon()
        self.sim = Simulation(bodies, config)
        self.sim.simulate(5)

    def test_returns_times_and_positions_per_body(self):
        times, positions = Visualization.extract_trajectories(self.sim.history)
        self.assertEqual(len(times), 6)
        self.assertIn("Earth", positions)
        self.assertIn("Moon", positions)
        self.assertEqual(positions["Earth"].shape, (6, 3))
        self.assertEqual(positions["Moon"].shape, (6, 3))

    def test_positions_match_history(self):
        _, positions = Visualization.extract_trajectories(self.sim.history)
        for step, snapshot in enumerate(self.sim.history):
            for body_snapshot in snapshot["bodies"]:
                self.assertTrue(np.array_equal(positions[body_snapshot["name"]][step],
                                                body_snapshot["position"]))

    def test_raises_on_empty_history(self):
        with self.assertRaises(ValueError):
            Visualization.extract_trajectories([])


class Test_AutoBodyScale(unittest.TestCase):

    def setUp(self):
        bodies, config = create_earth_moon()
        self.bodies = bodies
        self.sim = Simulation(bodies, config)
        self.sim.simulate(5)
        _, self.positions = Visualization.extract_trajectories(self.sim.history)

    def test_returns_positive_scale(self):
        scale = Visualization.auto_body_scale(self.bodies, self.positions)
        self.assertGreater(scale, 0.0)

    def test_largest_body_covers_target_fraction_of_extent(self):
        scale = Visualization.auto_body_scale(self.bodies, self.positions, visible_fraction=0.05)
        extent = Visualization._planar_extent(self.bodies, self.positions)
        max_radius = max(body.radius for body in self.bodies)
        self.assertAlmostEqual(max_radius * scale, 0.05 * extent)


class Test_AnimateSystem(unittest.TestCase):

    def setUp(self):
        bodies, config = create_earth_moon()
        self.bodies = bodies
        self.sim = Simulation(bodies, config)
        self.sim.simulate(10)

    def tearDown(self):
        plt.close("all")

    def test_returns_func_animation(self):
        anim = Visualization.animate_system(self.bodies, self.sim.history)
        self.assertIsInstance(anim, FuncAnimation)

    def test_frame_step_reduces_frame_count(self):
        anim_full = Visualization.animate_system(self.bodies, self.sim.history, frame_step=1)
        anim_sparse = Visualization.animate_system(self.bodies, self.sim.history, frame_step=5)
        full_frames = len(list(anim_full.new_frame_seq()))
        sparse_frames = len(list(anim_sparse.new_frame_seq()))
        self.assertGreater(full_frames, sparse_frames)


class Test_PlotDistanceOverTime(unittest.TestCase):

    def setUp(self):
        bodies, config = create_cannon_shot(Constants.CANNON_SPEEDS[2], Constants.CANNON_LEAD_ANGLES[0])
        self.bodies = bodies
        self.sim = Simulation(bodies, config)
        self.sim.simulate(5)

    def tearDown(self):
        plt.close("all")

    def test_plots_correct_distance(self):
        ax = Visualization.plot_distance_over_time(self.sim.history, "Earth", "Projectile",
                                                    unit=1.0, unit_label="m")
        line = ax.get_lines()[0]
        _, positions = Visualization.extract_trajectories(self.sim.history)
        expected = np.linalg.norm(positions["Earth"] - positions["Projectile"], axis=1)
        self.assertTrue(np.allclose(line.get_ydata(), expected))

    def test_draws_collision_marker_when_requested(self):
        ax = Visualization.plot_distance_over_time(self.sim.history, "Earth", "Projectile",
                                                    collision_distance=Constants.EARTH_RADIUS)
        self.assertEqual(len(ax.get_lines()), 2)

    def test_raises_for_unknown_body_name(self):
        with self.assertRaises(KeyError):
            Visualization.plot_distance_over_time(self.sim.history, "Earth", "Nonexistent")


if __name__ == '__main__':
    unittest.main()
