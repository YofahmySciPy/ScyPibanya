import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import integrator
from body import Body
from constants import G

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
        integrator.Verlet().calculate_acceleration(self.bodies[:3])
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
        integrator.Verlet().calculate_acceleration(self.bodies[:2])
        self.assertEqual(self.bodies[0].acceleration[0], 6*G/125.0)
        self.assertEqual(self.bodies[0].acceleration[1], 8*G/125.0)
        self.assertEqual(self.bodies[0].acceleration[2], 0.0)
        self.assertEqual(self.bodies[1].acceleration[0], -3*G/125.0)
        self.assertEqual(self.bodies[1].acceleration[1], -4*G/125.0)
        self.assertEqual(self.bodies[1].acceleration[2], 0.0)

    def test_calculation_of_acceleration_with_1_body(self):
        integrator.Verlet().calculate_acceleration([self.bodies[0]])
        self.assertEqual(self.bodies[0].acceleration[0], 0.0)
        self.assertEqual(self.bodies[0].acceleration[1], 0.0)
        self.assertEqual(self.bodies[0].acceleration[2], 0.0)

    def test_calculation_of_acceleration_with_0_bodies(self):
        integrator.Verlet().calculate_acceleration([])
        # no error should be raised, and nothing should happen

    def test_newtons_third_law(self):
        integrator.Verlet().calculate_acceleration(self.bodies[:2])
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
        integrator.Verlet().calculate_acceleration(self.bodies[:2])
        integrator.Verlet().step(self.bodies[:2], 1.0)
        # after one step, the bodies should have moved slightly towards each other
        self.assertTrue(np.linalg.norm(self.bodies[0].position) > 0.0)
        self.assertTrue(np.linalg.norm(self.bodies[1].position) < np.linalg.norm([1.0, 1.0, 0.0]))

    def test_step_does_not_move_single_body(self):
        integrator.Verlet().calculate_acceleration(self.bodies[:1])
        integrator.Verlet().step(self.bodies[:1], 1.0)
        # body should not move since there are no forces acting on it
        self.assertTrue(np.linalg.norm(self.bodies[0].position) == 0.0)

    def test_step_with_empty_bodies_raises_no_error(self):
        integrator.Verlet().calculate_acceleration([])
        integrator.Verlet().step([], 1.0)
        # no error should be raised, and nothing should happen

    def test_multiple_steps_decrease_distance(self):
        distance_before = np.linalg.norm(self.bodies[1].position - self.bodies[0].position)
        for i in range(1, 100):
            integrator.Verlet().step(self.bodies[:2], 100.0)
        distance_after = np.linalg.norm(self.bodies[1].position - self.bodies[0].position)
        self.assertLess(distance_after, distance_before)


    def test_energy_is_conserved_over_multiple_steps(self):
        verlet = integrator.Verlet()

        E_kin_before = sum(b.kinetic_energy() for b in self.bodies[:2])
        E_pot_before = verlet.potential_energy(self.bodies[:2])
        E_total_before = E_kin_before + E_pot_before

        for i in range(1, 100):
            verlet.step(self.bodies[:2], dt=1.0)

        E_kin_after = sum(b.kinetic_energy() for b in self.bodies[:2])
        E_pot_after = verlet.potential_energy(self.bodies[:2])
        E_total_after = E_kin_after + E_pot_after

        relative_change = abs(E_total_after - E_total_before) / abs(E_total_before)
        self.assertLess(relative_change, 0.01)



    def test_momentum_is_conserved_over_multiple_steps(self):
        verlet = integrator.Verlet()

        def total_momentum(bodies):
            return sum((b.mass * b.velocity for b in bodies), start=np.zeros(3))

        p_before = total_momentum(self.bodies[:2])

        for _ in range(100):
            verlet.step(self.bodies[:2], dt=1.0)

        p_after = total_momentum(self.bodies[:2])

        np.testing.assert_allclose(p_after, p_before, atol=1e-9)

    def test_time_reversal_returns_to_initial_position(self):
        verlet = integrator.Verlet()
        start_positions = [b.position.copy() for b in self.bodies[:2]]

        for _ in range(50):
            verlet.step(self.bodies[:2], dt=1.0)

        for b in self.bodies[:2]:
            b.velocity = -b.velocity
            b.position_previous = None  # forces new Euler-Init in opposite direction

        for _ in range(50):
            verlet.step(self.bodies[:2], dt=1.0)

        for b, start in zip(self.bodies[:2], start_positions):
            np.testing.assert_allclose(b.position, start, atol=1e-3)

    def test_circular_orbit_returns_to_starting_position(self):
        verlet = integrator.Verlet()
        # ATTENTION: Mass of earth is being raised synthetically to fixate it. This was,
        # the sole calculation of the circular path can be tested.
        # In reality, the orbit isn't a circle, but this would be hard to test.
        earth = Body("Earth", mass=5.972e30, radius=6.371e6,
                     position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0])
        r = 3.844e8  # distance from earth to moon
        v = np.sqrt(G * earth.mass / r)  # circular path velocity
        moon = Body("Moon", mass=7.348e22, radius=1.737e6,
                    position=[r, 0.0, 0.0], velocity=[0.0, v, 0.0])
        bodies = [earth, moon]

        start = moon.position.copy()
        T = 2 * np.pi * np.sqrt(r**3 / (G * earth.mass))
        steps = 10000
        dt = T / steps

        for _ in range(steps):
            verlet.step(bodies, dt=dt)

        np.testing.assert_allclose(moon.position, start, atol=r*0.05)

    def test_smaller_dt_is_more_accurate(self):
        def run(steps, total_time):
            # The mass of the earth got raised synthetically here
            earth = Body("Earth", mass=5.972e30, radius=6.371e6,
                         position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0])
            r = 3.844e8
            v = np.sqrt(G * earth.mass / r)
            moon = Body("Moon", mass=7.348e22, radius=1.737e6,
                        position=[r, 0.0, 0.0], velocity=[0.0, v, 0.0])
            bodies = [earth, moon]
            verlet = integrator.Verlet()
            dt = total_time / steps
            for _ in range(steps):
                verlet.step(bodies, dt=dt)
            return moon.position.copy()

        r = 3.844e8
        # The mass of the earth got raised synthetically here again
        earth_mass = 5.972e30
        T = 2 * np.pi * np.sqrt(r**3 / (G * earth_mass))
        start = np.array([r, 0.0, 0.0])

        coarse = run(100, T)
        fine = run(10000, T)

        error_coarse = np.linalg.norm(coarse - start)
        error_fine = np.linalg.norm(fine - start)

        self.assertLess(error_fine, error_coarse)





class TestEulerIntegrator(unittest.TestCase):
    def setUp(self):
        # create a simple two-body system for testing
        bodies = [
            Body("Body1", mass=1.0, radius=0.5, position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0]),
            Body("Body2", mass=2.0, radius=1.0, position=[3.0, 4.0, 0.0], velocity=[0.0, 0.0, 0.0])
        ]
        self.bodies = bodies


    def test_step_moves_bodies_towards_each_other(self):
        euler = integrator.Euler()
        for _ in range(100):
            euler.step(self.bodies[:2], dt=1.0)
        # Bodies should attract each other
        self.assertLess(
            # Distance gets smaller
            np.linalg.norm(self.bodies[1].position - self.bodies[0].position),
            np.linalg.norm([3.0, 4.0, 0.0])
        )

    def test_step_does_not_move_single_body(self):
        euler = integrator.Euler()
        euler.step(self.bodies[:1], dt=1.0)
        # without other bodies there are no forces so no movement
        np.testing.assert_array_equal(self.bodies[0].position, [0.0, 0.0, 0.0])

    def test_step_with_empty_bodies_raises_no_error(self):
        euler = integrator.Euler()
        # should not crash
        euler.step([], dt=1.0)

    def test_velocity_updates_with_acceleration(self):
        euler = integrator.Euler()
        euler.step(self.bodies[:2], dt=1.0)
        # Bodies were at rest so after one step their velocity should not be zero
        self.assertGreater(np.linalg.norm(self.bodies[0].velocity), 0.0)

    def test_momentum_is_conserved_over_multiple_steps(self):
        euler = integrator.Euler()

        def total_momentum(bodies):
            return sum((b.mass * b.velocity for b in bodies), start=np.zeros(3))

        p_before = total_momentum(self.bodies[:2])
        for _ in range(100):
            euler.step(self.bodies[:2], dt=1.0)
        p_after = total_momentum(self.bodies[:2])

        np.testing.assert_allclose(p_after, p_before, atol=1e-6)

    def test_energy_drifts_over_many_steps(self):
    # Quintessential about explicit Euler: he is NOT conserving energy.
    # He is spiraling outwards on a small circular orbit.
        euler = integrator.Euler()
        earth = Body("Earth", mass=1e30, radius=6.371e6,
                     position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0])
        r = 3.844e8
        v = np.sqrt(G * earth.mass / r)
        moon = Body("Moon", mass=7.348e22, radius=1.737e6,
                    position=[r, 0.0, 0.0], velocity=[0.0, v, 0.0])
        bodies = [earth, moon]

        T = 2 * np.pi * np.sqrt(r**3 / (G * earth.mass))
        steps = 1000
        dt = T / steps

        r_start = np.linalg.norm(moon.position - earth.position)
        for _ in range(steps):
            euler.step(bodies, dt=dt)
        r_end = np.linalg.norm(moon.position - earth.position)

        # Path is spiraling outwards, distance should increase
        self.assertGreater(r_end, r_start)

class TestVerletVsEuler(unittest.TestCase):
    def setUp(self):
        pass

    def test_euler_drifts_more_than_verlet(self):
    # same circular orbit, same dt -> Verlet stays closer to the actual distance
        def run(integrator):
            earth = Body("Earth", mass=1e30, radius=6.371e6,
                         position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0])
            r = 3.844e8
            v = np.sqrt(G * earth.mass / r)
            moon = Body("Moon", mass=7.348e22, radius=1.737e6,
                        position=[r, 0.0, 0.0], velocity=[0.0, v, 0.0])
            bodies = [earth, moon]
            T = 2 * np.pi * np.sqrt(r**3 / (G * earth.mass))
            steps = 1000
            dt = T / steps
            for _ in range(steps):
                integrator.step(bodies, dt=dt)
            return abs(np.linalg.norm(moon.position - earth.position) - r)

        error_euler = run(integrator.Euler())
        error_verlet = run(integrator.Verlet())
        self.assertGreater(error_euler, error_verlet)







if __name__ == '__main__':
    unittest.main()
