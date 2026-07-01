import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import constants
from integrator import Verlet, Euler
from scenarios import create_earth_moon, create_cannon_shot
from simulation import Simulation

class Test_Simulation_EarthMoon_Verlet(unittest.TestCase):

    def setUp(self):
        self.sim = Simulation.build_simulation(cannon=False, duration=1) # duration input is days, it will be converted to seconds

    def test_init(self):
        self.assertEqual(self.sim.t, 0.0)
        self.assertEqual(self.sim.dt, constants.HOUR) # one step takes one hour
        self.assertEqual(len(self.sim.history), 1)
        self.assertIn("t", self.sim.history[0])
        self.assertIn("bodies", self.sim.history[0])
        for body_snapshot in self.sim.history[0]["bodies"]:
            self.assertIn("name", body_snapshot)
            self.assertIn("mass", body_snapshot)
            self.assertIn("radius", body_snapshot)
            self.assertIn("position", body_snapshot)
            self.assertIn("velocity", body_snapshot)
        self.assertEqual(self.sim.history[0]["t"], 0.0)
        self.assertEqual(len(self.sim.bodies), 2)
        self.assertIsInstance(self.sim.integrator, Verlet)

    def test_step(self):
        pos_before = self.sim.bodies[1].position.copy()
        self.sim.step()
        self.assertEqual(len(self.sim.history), 2)
        self.assertEqual(self.sim.t, constants.HOUR) # after one step, one hour passed
        self.assertIn("t", self.sim.history[1])
        self.assertIn("bodies", self.sim.history[1])
        for body_snapshot in self.sim.history[0]["bodies"]:
            self.assertIn("name", body_snapshot)
            self.assertIn("mass", body_snapshot)
            self.assertIn("radius", body_snapshot)
            self.assertIn("position", body_snapshot)
            self.assertIn("velocity", body_snapshot)
        self.assertEqual(self.sim.history[1]["bodies"][0]["name"], "Earth")
        self.assertEqual(self.sim.history[1]["bodies"][1]["name"], "Moon")
        self.assertFalse(np.array_equal(pos_before, self.sim.bodies[1].position))

    def test_simulate(self):
        self.sim.simulate()
        self.assertEqual(len(self.sim.history), 25) # after one day: 24 Steps(one each hour) + 1 initial step
        self.assertAlmostEqual(self.sim.t, constants.DAY) # one day is passed

class Test_Simulation_Cannon_Euler(unittest.TestCase):

    def setUp(self):
        self.sim = Simulation.build_simulation(cannon=True, duration=1, integrator=Euler(), cannonball_angle=0, cannonball_speed=12000) # duration input is days, it will be converted to seconds

    def test_init(self):
        self.assertEqual(self.sim.t, 0.0)
        self.assertEqual(self.sim.dt, 10 * constants.SECOND) # one step takes 10 seconds
        self.assertEqual(len(self.sim.history), 1)
        self.assertIn("t", self.sim.history[0])
        self.assertIn("bodies", self.sim.history[0])
        for body_snapshot in self.sim.history[0]["bodies"]:
            self.assertIn("name", body_snapshot)
            self.assertIn("mass", body_snapshot)
            self.assertIn("radius", body_snapshot)
            self.assertIn("position", body_snapshot)
            self.assertIn("velocity", body_snapshot)
        self.assertEqual(self.sim.history[0]["t"], 0.0)
        self.assertEqual(len(self.sim.bodies), 3)
        self.assertIsInstance(self.sim.integrator, Euler)

    def test_step(self):
        pos_before = self.sim.bodies[1].position.copy()
        self.sim.step()
        self.assertEqual(len(self.sim.history), 2)
        self.assertEqual(self.sim.t, 10 * constants.SECOND) # after ten seconds, one step is passed
        self.assertIn("t", self.sim.history[1])
        self.assertIn("bodies", self.sim.history[1])
        for body_snapshot in self.sim.history[0]["bodies"]:
            self.assertIn("name", body_snapshot)
            self.assertIn("mass", body_snapshot)
            self.assertIn("radius", body_snapshot)
            self.assertIn("position", body_snapshot)
            self.assertIn("velocity", body_snapshot)
        self.assertEqual(self.sim.history[1]["bodies"][0]["name"], "Earth")
        self.assertEqual(self.sim.history[1]["bodies"][1]["name"], "Moon")
        self.assertEqual(self.sim.history[1]["bodies"][2]["name"], "Projectile")
        self.assertFalse(np.array_equal(pos_before, self.sim.bodies[1].position))

    def test_simulate(self):
        self.sim.simulate()
        self.assertEqual(len(self.sim.history), 8641) # after one day: 8640 steps(one each ten seconds) + 1 initial step
        self.assertAlmostEqual(self.sim.t, constants.DAY) # one day is passed

class Test_Value_Error(unittest.TestCase):

    def test_value_error(self):
        with self.assertRaises(ValueError):
            Simulation.build_simulation(cannon=True, duration=1) # duration input is days, it will be converted to seconds

if __name__ == '__main__':
    unittest.main()