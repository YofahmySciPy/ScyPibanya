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

    def test_step_moves_bodies_towards_each_other(self):
        Integrator.Verlet().calculate_acceleration(self.bodies[:2])
        Integrator.Verlet().step(self.bodies[:2], 1.0)
        # after one step, the bodies should have moved slightly towards each other
        self.assertTrue(np.linalg.norm(self.bodies[0].position) > 0.0)
        self.assertTrue(np.linalg.norm(self.bodies[1].position) < np.linalg.norm([1.0, 1.0, 0.0]))

    def test_step_does_not_move_single_body(self):
        Integrator.Verlet().calculate_acceleration(self.bodies[:1])
        Integrator.Verlet().step(self.bodies[:1], 1.0)
        # body should not move since there are no forces acting on it
        self.assertTrue(np.linalg.norm(self.bodies[0].position) == 0.0)

    def test_step_with_empty_bodies_raises_no_error(self):
        Integrator.Verlet().calculate_acceleration([])
        Integrator.Verlet().step([], 1.0)
        # no error should be raised, and nothing should happen

    def test_multiple_steps_decrease_distance(self):
        for i in range(1, 100):
            Integrator.Verlet().calculate_acceleration(self.bodies[:2])
            Integrator.Verlet().step(self.bodies[:2], 3600.0)
            print(self.bodies[0].distance_to(self.bodies[1]))
        # after 100 steps, the bodies should have moved significantly towards each other


    def test_energy_is_conserved_over_multiple_steps(self):
        # this is a very rough test, since Verlet is not perfectly energy-conserving, but the total energy should not change drastically over a few steps
        pass

    def test_momentum_is_conserved_over_multiple_steps(self):
        # 
        pass

    def test_time_reversal_returns_to_initial_position(self):
        # if we run the simulation forward for a few steps, and then reverse the velocities and run it backward for the same number of steps, we should end up back at the initial positions (within numerical precision limits)
        pass

    def test_circular_orbit_returns_to_starting_position(self):
        # if we set up a circular orbit and run the simulation for one full orbital period, we should end up back at the starting position (within numerical precision limits)
        pass

    def test_smaller_dt_is_more_accurate(self):
        # if we run the simulation with a smaller time step, we should get a result that is closer to the expected analytical solution (for example, for a circular orbit, the radius should remain more constant)
        pass





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
