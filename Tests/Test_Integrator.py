import unittest
import numpy as np
import Integrator
from Body import Body
from Constants import G

class TestIntegrator(unittest.TestCase):
    def setUp(self):
        # create a simple two-body system for testing
        bodies = [
            Body("Body1", mass=1.0, radius=0.5, position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0]),
            Body("Body2", mass=2.0, radius=1.0, position=[3.0, 4.0, 0.0], velocity=[0.0, 0.0, 0.0]),
            Body("Body3",mass=3.0, radius=1.0, position=[1.0, 1.0, 0.0], velocity=[0.0, 0.0, 0.0])
        ]
        self.bodies = bodies

    def test_calculation_of_acceleration_with_3_distant_bodies(self):
        Integrator.Verlet().calculate_acceleration(self.bodies[:3])
        self.assertAlmostEqual(self.bodies[0].acceleration[0]/G, 1.1086601717798212)
        self.assertAlmostEqual(self.bodies[0].acceleration[1]/G, 1.1246601717798212)
        self.assertAlmostEqual(self.bodies[0].acceleration[2]/G, 0.0)
        self.assertAlmostEqual(self.bodies[1].acceleration[0]/G, -0.15200773759043755)
        self.assertAlmostEqual(self.bodies[1].acceleration[1]/G, -0.22401160638565633)
        self.assertAlmostEqual(self.bodies[1].acceleration[2]/G, 0.0)
        self.assertAlmostEqual(self.bodies[2].acceleration[0]/G, -0.26821489886631534)
        self.assertAlmostEqual(self.bodies[2].acceleration[1]/G, -0.22554565300283618)
        self.assertAlmostEqual(self.bodies[2].acceleration[2]/G, 0.0)

    def test_calculation_of_acceleration_with_2_distant_bodies(self):
        Integrator.Verlet().calculate_acceleration(self.bodies[:2])
        self.assertEqual(self.bodies[0].acceleration[0], 6*G/125.0)
        self.assertEqual(self.bodies[0].acceleration[1], 8*G/125.0)
        self.assertEqual(self.bodies[0].acceleration[2], 0.0)
        self.assertEqual(self.bodies[1].acceleration[0], -3*G/125.0)
        self.assertEqual(self.bodies[1].acceleration[1], -4*G/125.0)
        self.assertEqual(self.bodies[1].acceleration[2], 0.0)

    def test_calculation_of_acceleration_with_1_body(self):
        Integrator.Verlet().calculate_acceleration([self.bodies[0]])
        self.assertEqual(self.bodies[0].acceleration[0], 0.0)
        self.assertEqual(self.bodies[0].acceleration[1], 0.0)
        self.assertEqual(self.bodies[0].acceleration[2], 0.0)

    def test_calculation_of_acceleration_with_0_bodies(self):
        Integrator.Verlet().calculate_acceleration([])
        # no error should be raised, and nothing should happen

    def test_newtons_third_law(self):
        Integrator.Verlet().calculate_acceleration(self.bodies[:2])
        # the forces should be equal and opposite, so the accelerations should be in the same ratio as the masses
        a1 = self.bodies[0].acceleration
        a2 = self.bodies[1].acceleration
        m1 = self.bodies[0].mass
        m2 = self.bodies[1].mass
        self.assertTrue(np.allclose(a1 * m1, -a2 * m2))



class TestVerletIntegrator(unittest.TestCase):

    def setUp(self):
        # create a simple two-body system for testing
        bodies = [
            Body("Body1", mass=1.0, radius=0.5, position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0]),
            Body("Body2", mass=2.0, radius=1.0, position=[1.0, 1.0, 0.0], velocity=[0.0, 0.0, 0.0])
        ]
        self.bodies = bodies







class TestEulerIntegrator(unittest.TestCase):
    def setup(self):
        # create a simple two-body system for testing
        bodies = [
            Body("Body1", mass=1.0, radius=0.5, position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0]),
            Body("Body2", mass=2.0, radius=1.0, position=[1.0, 1.0, 0.0], velocity=[0.0, 0.0, 0.0])
        ]
        self.bodies = bodies
        pass

    pass







if __name__ == '__main__':
    unittest.main()
