import unittest
import sys
import os

import numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(__file__) , "../src"))

import Constants
from Simulation import Simulation
from Scenarios import create_earth_moon, create_cannon_shot
from Integrator import Verlet, Euler

class Test_Simulation_EarthMoon_Verlet(unittest.TestCase):

    def setUp(self):
        self.sim = Simulation(cannon=False, duration=1) # duration input is days, it will be converted to seconds

    def test_init(self):
        self.assertEqual(self.sim.t, 0.0)
        self.assertEqual(self.sim.dt, Constants.HOUR) # one step takes one hour
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
        self.assertEqual(self.sim.t, Constants.HOUR) # after one step, one hour passed
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
        self.assertAlmostEqual(self.sim.t, Constants.DAY) # one day is passed

class Test_Simulation_Cannon_Euler(unittest.TestCase):

    def setUp(self):
        self.sim = Simulation(cannon=True, duration=1, integrator=Euler(), cannon_angle=0, cannonball_speed=100) # duration input is days, it will be converted to seconds

    def test_init(self):
        self.assertEqual(self.sim.t, 0.0)
        self.assertEqual(self.sim.dt, Constants.MINUTE) # one step takes one minute
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
        self.assertEqual(self.sim.t, Constants.MINUTE) # after one minute, one step is passed
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
        self.assertEqual(len(self.sim.history), 1441) # after one day: 1440 steps(one each minute) + 1 initial step
        self.assertAlmostEqual(self.sim.t, Constants.DAY) # one day is passed

class Test_Value_Error(unittest.TestCase):

    def test_value_error(self):
        with self.assertRaises(ValueError):
            Simulation(cannon=True, duration=1) # duration input is days, it will be converted to seconds

if __name__ == '__main__':
    unittest.main()