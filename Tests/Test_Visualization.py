import os
import sys
import unittest

import matplotlib
matplotlib.use("Agg")  # headless backend - no display needed for the tests
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from Body import Body
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

    def test_raises_on_no_bodies(self):
        with self.assertRaises(ValueError):
            Visualization.auto_body_scale([], self.positions)

    def test_raises_on_non_positive_radius(self):
        broken_body = Body("Broken", mass=1.0, radius=1.0, position=[0, 0, 0], velocity=[0, 0, 0])
        broken_body.radius = 0.0
        with self.assertRaises(ValueError):
            Visualization.auto_body_scale([broken_body], self.positions)


class Test_PlotSystem(unittest.TestCase):

    def setUp(self):
        bodies, config = create_earth_moon()
        self.bodies = bodies
        self.sim = Simulation(bodies, config)
        self.sim.simulate(5)

    def tearDown(self):
        plt.close("all")

    def test_returns_axes_with_one_circle_per_body(self):
        ax = Visualization.plot_system(self.bodies, self.sim.history)
        circles = [patch for patch in ax.patches]
        self.assertEqual(len(circles), len(self.bodies))

    def test_accepts_explicit_body_scale(self):
        ax = Visualization.plot_system(self.bodies, self.sim.history, body_scale=500.0)
        circle = ax.patches[0]
        assert isinstance(circle, Circle)
        expected_radius = self.bodies[0].radius * 500.0 / Constants.KM
        self.assertAlmostEqual(circle.get_radius(), expected_radius)

    def test_raises_on_non_positive_body_scale(self):
        with self.assertRaises(ValueError):
            Visualization.plot_system(self.bodies, self.sim.history, body_scale=0.0)

    def test_can_draw_into_existing_axes(self):
        _, ax = plt.subplots()
        returned_ax = Visualization.plot_system(self.bodies, self.sim.history, ax=ax)
        self.assertIs(returned_ax, ax)


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

    def test_raises_on_non_positive_frame_step(self):
        with self.assertRaises(ValueError):
            Visualization.animate_system(self.bodies, self.sim.history, frame_step=0)


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


class Test_InteractiveSystem(unittest.TestCase):

    def setUp(self):
        bodies, config = create_earth_moon()
        self.bodies = bodies
        self.sim = Simulation(bodies, config)
        self.sim.simulate(5)

    def tearDown(self):
        plt.close("all")

    def test_returns_figure_and_slider_that_rescales_circles(self):
        fig, slider = Visualization.interactive_system(self.bodies, self.sim.history)
        ax = fig.axes[0]
        circles = [patch for patch in ax.patches if isinstance(patch, Circle)]
        circles_before = [circle.get_radius() for circle in circles]

        slider.set_val(slider.valmax)

        circles_after = [circle.get_radius() for circle in circles]
        self.assertTrue(all(after > before for before, after in zip(circles_before, circles_after)))


if __name__ == '__main__':
    unittest.main()
