import unittest
import sys
import os

import numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(__file__) , "../src"))

from Simulation import Simulation
from Scenarios import create_earth_moon, create_cannon_shot
from Integrator import Verlet, Euler

class Test_Simulation_EarthMoon_Verlet(unittest.TestCase):

    def setUp(self):
        bodies, config = create_earth_moon()
        self.sim = Simulation(bodies, config)

    def test_init(self):
        self.assertEqual(self.sim.t, 0.0)
        self.assertEqual(self.sim.dt, 60.0)
        self.assertEqual(len(self.sim.history), 1)
        self.assertIn("t", self.sim.history[0])
        self.assertIn("bodies", self.sim.history[0])
        for body_snapshot in self.sim.history[0]["bodies"]:
            self.assertIn("name", body_snapshot)
            self.assertIn("mass", body_snapshot)
            self.assertIn("position", body_snapshot)
            self.assertIn("velocity", body_snapshot)
        self.assertEqual(self.sim.history[0]["t"], 0.0)
        self.assertEqual(len(self.sim.bodies), 2)
        self.assertIsInstance(self.sim.integrator, Verlet)

    def test_step(self):
        pos_before = self.sim.bodies[1].position.copy()
        self.sim.step()
        self.assertEqual(len(self.sim.history), 2)
        self.assertEqual(self.sim.t, 60.0)
        self.assertIn("t", self.sim.history[1])
        self.assertIn("bodies", self.sim.history[1])
        for body_snapshot in self.sim.history[0]["bodies"]:
            self.assertIn("name", body_snapshot)
            self.assertIn("mass", body_snapshot)
            self.assertIn("position", body_snapshot)
            self.assertIn("velocity", body_snapshot)
        self.assertEqual(self.sim.history[1]["bodies"][0]["name"], "Earth")
        self.assertEqual(self.sim.history[1]["bodies"][1]["name"], "Moon")
        self.assertFalse(np.array_equal(pos_before, self.sim.bodies[1].position))

    def test_simulate(self):
        self.sim.simulate(10)
        self.assertEqual(len(self.sim.history), 11)
        self.assertAlmostEqual(self.sim.t, 10 * self.sim.dt)

class Test_Simulation_Cannon_Euler(unittest.TestCase):

    def setUp(self):
        bodies, config = create_cannon_shot(100, 0)
        self.sim = Simulation(bodies, config, Euler())

    def test_init(self):
        self.assertEqual(self.sim.t, 0.0)
        self.assertEqual(self.sim.dt, 1.0)
        self.assertEqual(len(self.sim.history), 1)
        self.assertIn("t", self.sim.history[0])
        self.assertIn("bodies", self.sim.history[0])
        for body_snapshot in self.sim.history[0]["bodies"]:
            self.assertIn("name", body_snapshot)
            self.assertIn("mass", body_snapshot)
            self.assertIn("position", body_snapshot)
            self.assertIn("velocity", body_snapshot)
        self.assertEqual(self.sim.history[0]["t"], 0.0)
        self.assertEqual(len(self.sim.bodies), 3)
        self.assertIsInstance(self.sim.integrator, Euler)

    def test_step(self):
        pos_before = self.sim.bodies[1].position.copy()
        self.sim.step()
        self.assertEqual(len(self.sim.history), 2)
        self.assertEqual(self.sim.t, 1.0)
        self.assertIn("t", self.sim.history[1])
        self.assertIn("bodies", self.sim.history[1])
        for body_snapshot in self.sim.history[0]["bodies"]:
            self.assertIn("name", body_snapshot)
            self.assertIn("mass", body_snapshot)
            self.assertIn("position", body_snapshot)
            self.assertIn("velocity", body_snapshot)
        self.assertEqual(self.sim.history[1]["bodies"][0]["name"], "Earth")
        self.assertEqual(self.sim.history[1]["bodies"][1]["name"], "Moon")
        self.assertEqual(self.sim.history[1]["bodies"][2]["name"], "Projectile")
        self.assertFalse(np.array_equal(pos_before, self.sim.bodies[1].position))

    def test_simulate(self):
        self.sim.simulate(10)
        self.assertEqual(len(self.sim.history), 11)
        self.assertAlmostEqual(self.sim.t, 10 * self.sim.dt)

if __name__ == '__main__':
    unittest.main()
