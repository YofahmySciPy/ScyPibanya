# KI-GENERIERTE TESTS MIT OPUS 4.8


"""
tests fuer die Collisions-Klasse.

Designprinzip dieser tests: Jeder Test waehlt seine Werte so, dass ein
Bestehen die ALLGEMEINE Korrektheit der Formel belegt -- nicht nur einen
guenstigen Einzelfall. Konkret:
  - Positionen/Geschwindigkeiten sind voll 3D (x, y UND z besetzt),
    damit ein Bug in einer Komponente nicht unbemerkt bleibt.
  - Massen sind ungleich, damit Massengewichtungen wirklich geprueft werden.
  - Radien sind != 1, weil 1^3 == 1 die dritte Potenz "verstecken" wuerde.
  - Beide Koerper liegen NICHT im Ursprung, sonst verschwindet ein Term.

HINWEIS: make_body / Body-Konstruktor ggf. an eure echte Body-Klasse anpassen.
"""
import os
import sys
import unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from body import Body
from collisions import Collisions


DT = 0.01


def make_body(name, mass, position, velocity, radius):
    return Body(name=name,
                mass=mass,
                position=np.array(position, dtype=float),
                velocity=np.array(velocity, dtype=float),
                radius=radius)


def total_momentum(bodies):
    return sum((b.mass * b.velocity for b in bodies), start=np.zeros(3))


def total_mass(bodies):
    return sum(b.mass for b in bodies)


# ===========================================================================
# 1) Physik einer EINZELNEN Verschmelzung (merge)
# ===========================================================================
class TestMergePhysics(unittest.TestCase):

    def test_mass_is_summed(self):
        b1 = make_body("Earth", 2.0, [1, 2, 3], [0, 0, 0], 2.0)
        b2 = make_body("Moon", 3.0, [4, 5, 6], [0, 0, 0], 3.0)
        merged = Collisions.merge(b1, b2, DT)
        self.assertAlmostEqual(merged.mass, 5.0)

    def test_velocity_is_mass_weighted_average_3d(self):
        b1 = make_body("Earth", 2.0, [0, 0, 0], [1, 4, -2], 1.0)
        b2 = make_body("Moon", 3.0, [1, 0, 0], [0, 1, 5], 1.0)
        merged = Collisions.merge(b1, b2, DT)
        # (2*[1,4,-2] + 3*[0,1,5]) / 5 = [2,11,11]/5
        np.testing.assert_allclose(merged.velocity, [0.4, 2.2, 2.2])

    def test_position_is_mass_weighted_center_3d(self):
        b1 = make_body("Earth", 1.0, [1, 2, 3], [0, 0, 0], 1.0)
        b2 = make_body("Moon", 3.0, [5, 6, 7], [0, 0, 0], 1.0)
        merged = Collisions.merge(b1, b2, DT)
        # (1*[1,2,3] + 3*[5,6,7]) / 4 = [16,20,24]/4 = [4,5,6]
        np.testing.assert_allclose(merged.position, [4.0, 5.0, 6.0])

    def test_radius_combines_by_volume(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 2.0)
        b2 = make_body("Moon", 1.0, [1, 0, 0], [0, 0, 0], 3.0)
        merged = Collisions.merge(b1, b2, DT)
        expected = (2.0**3 + 3.0**3) ** (1 / 3)   # = 35^(1/3)
        self.assertAlmostEqual(merged.radius, expected)

    def test_head_on_equal_momentum_gives_zero_velocity(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [1, -2, 3], 1.0)
        b2 = make_body("Moon", 1.0, [1, 0, 0], [-1, 2, -3], 1.0)
        merged = Collisions.merge(b1, b2, DT)
        np.testing.assert_allclose(merged.velocity, [0, 0, 0], atol=1e-12)

    def test_position_previous_consistent_with_velocity_3d(self):
        b1 = make_body("Earth", 2.0, [1, 2, 3], [1, 4, -2], 1.0)
        b2 = make_body("Moon", 3.0, [4, 5, 6], [0, 1, 5], 1.0)
        merged = Collisions.merge(b1, b2, DT)
        implied_v = (merged.position - merged.position_previous) / DT
        np.testing.assert_allclose(implied_v, merged.velocity)

    def test_merge_is_symmetric(self):
        b1 = make_body("Earth", 2.0, [1, 2, 3], [1, 0, -1], 2.0)
        b2 = make_body("Moon", 3.0, [4, 5, 6], [0, 2, 5], 3.0)
        m12 = Collisions.merge(b1, b2, DT)
        m21 = Collisions.merge(b2, b1, DT)
        self.assertAlmostEqual(m12.mass, m21.mass)
        self.assertAlmostEqual(m12.radius, m21.radius)
        np.testing.assert_allclose(m12.position, m21.position)
        np.testing.assert_allclose(m12.velocity, m21.velocity)


# ===========================================================================
# 2) Kollisions-ERKENNUNG (Schwelle distance <= r1 + r2)
# ===========================================================================
class TestCollisionDetection(unittest.TestCase):

    def test_clearly_inside_merges(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 1.0)
        b2 = make_body("Moon", 1.0, [1, 0, 0], [0, 0, 0], 1.0)   # Abstand 1 < 2
        self.assertEqual(len(Collisions.handle([b1, b2], DT)), 1)

    def test_exact_boundary_merges(self):
        # Abstand == Summe der Radien (5 == 2+3)
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 2.0)
        b2 = make_body("Moon", 1.0, [5, 0, 0], [0, 0, 0], 3.0)
        self.assertEqual(len(Collisions.handle([b1, b2], DT)), 1)

    def test_just_outside_boundary_no_merge(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 2.0)
        b2 = make_body("Moon", 1.0, [5.001, 0, 0], [0, 0, 0], 3.0)
        self.assertEqual(len(Collisions.handle([b1, b2], DT)), 2)

    def test_clearly_outside_no_merge(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 1.0)
        b2 = make_body("Moon", 1.0, [100, 0, 0], [0, 0, 0], 1.0)
        self.assertEqual(len(Collisions.handle([b1, b2], DT)), 2)

    def test_detection_uses_full_3d_distance(self):
        # sqrt(2^2+3^2+6^2) = 7 == r1+r2 (3+4) -> Beruehrung
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 3.0)
        b2 = make_body("Moon", 1.0, [2, 3, 6], [0, 0, 0], 4.0)
        self.assertEqual(len(Collisions.handle([b1, b2], DT)), 1)

    def test_3d_diagonal_just_outside_no_merge(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 3.0)
        b2 = make_body("Moon", 1.0, [2, 3, 6.002], [0, 0, 0], 4.0)  # Abstand > 7
        self.assertEqual(len(Collisions.handle([b1, b2], DT)), 2)


# ===========================================================================
# 3) MEHRERE Koerper: Ketten UND getrennte gleichzeitige Kollisionen
# ===========================================================================
class TestMultipleBodies(unittest.TestCase):

    def test_only_colliding_pair_merges(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 1.0)
        b2 = make_body("Moon", 1.0, [1, 0, 0], [0, 0, 0], 1.0)
        b3 = make_body("Projectile", 1.0, [100, 0, 0], [0, 0, 0], 1.0)
        self.assertEqual(len(Collisions.handle([b1, b2, b3], DT)), 2)

    def test_lonely_body_survives_as_same_object(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 1.0)
        b2 = make_body("Moon", 1.0, [1, 0, 0], [0, 0, 0], 1.0)
        b3 = make_body("Projectile", 1.0, [100, 0, 0], [5, 0, 0], 1.0)
        result = Collisions.handle([b1, b2, b3], DT)
        self.assertIn(b3, result)

    def test_chain_three_bodies_merge_into_one(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 1.0)
        b2 = make_body("Moon", 1.0, [1, 0, 0], [0, 0, 0], 1.0)
        b3 = make_body("Projectile", 1.0, [2, 0, 0], [0, 0, 0], 1.0)
        self.assertEqual(len(Collisions.handle([b1, b2, b3], DT)), 1)

    def test_two_separate_pairs_merge_independently(self):
        a1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 1.0)
        a2 = make_body("Moon", 1.0, [1, 0, 0], [0, 0, 0], 1.0)   # Paar A
        b1 = make_body("Projectile", 1.0, [50, 0, 0], [0, 0, 0], 1.0)
        b2 = make_body("Comet", 1.0, [51, 0, 0], [0, 0, 0], 1.0)  # Paar B
        self.assertEqual(len(Collisions.handle([a1, a2, b1, b2], DT)), 2)

    def test_three_body_merge_has_correct_mass_position_radius(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 2.0)
        b2 = make_body("Moon", 2.0, [1, 1, 0], [0, 0, 0], 2.0)
        b3 = make_body("Projectile", 3.0, [0, 1, 1], [0, 0, 0], 2.0)
        result = Collisions.handle([b1, b2, b3], DT)
        self.assertEqual(len(result), 1)
        merged = result[0]
        self.assertAlmostEqual(merged.mass, 6.0)
        # COM: (1*[0,0,0]+2*[1,1,0]+3*[0,1,1])/6 = [2,5,3]/6
        np.testing.assert_allclose(merged.position, np.array([2, 5, 3]) / 6)
        # Radius: (3 * 2^3)^(1/3) = 24^(1/3)
        self.assertAlmostEqual(merged.radius, (3 * 2.0**3) ** (1 / 3))


# ===========================================================================
# 4) ERHALTUNGSGROESSEN ueber das gesamte System
# ===========================================================================
class TestConservation(unittest.TestCase):

    def test_total_mass_conserved_mixed(self):
        bodies = [
            make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 1.0),
            make_body("Moon", 2.0, [1, 0, 0], [0, 0, 0], 1.0),
            make_body("Projectile", 3.0, [50, 0, 0], [0, 0, 0], 1.0),
        ]
        m_before = total_mass(bodies)
        self.assertAlmostEqual(total_mass(Collisions.handle(bodies, DT)), m_before)

    def test_total_momentum_conserved_3d_mixed(self):
        bodies = [
            make_body("Earth", 1.0, [0, 0, 0], [2, -1, 4], 1.0),
            make_body("Moon", 2.0, [1, 0, 0], [0, 3, -2], 1.0),
            make_body("Projectile", 3.0, [50, 0, 0], [1, 1, 1], 1.0),
        ]
        p_before = total_momentum(bodies)
        np.testing.assert_allclose(total_momentum(Collisions.handle(bodies, DT)),
                                   p_before)

    def test_momentum_conserved_when_all_merge_3d(self):
        bodies = [
            make_body("Earth", 1.0, [0, 0, 0], [1, 0, 0], 1.0),
            make_body("Moon", 1.0, [1, 0, 0], [0, 2, 0], 1.0),
            make_body("Projectile", 1.0, [2, 0, 0], [0, 0, 3], 1.0),
        ]
        p_before = total_momentum(bodies)
        result = Collisions.handle(bodies, DT)
        self.assertEqual(len(result), 1)
        np.testing.assert_allclose(total_momentum(result), p_before)

    def test_momentum_conserved_with_two_separate_pairs(self):
        bodies = [
            make_body("Earth", 1.0, [0, 0, 0], [2, 0, 0], 1.0),
            make_body("Moon", 1.0, [1, 0, 0], [0, 2, 0], 1.0),    # Paar A
            make_body("Projectile", 1.0, [50, 0, 0], [0, 0, 5], 1.0),
            make_body("Comet", 1.0, [51, 0, 0], [-3, 0, 0], 1.0),  # Paar B
        ]
        p_before = total_momentum(bodies)
        result = Collisions.handle(bodies, DT)
        self.assertEqual(len(result), 2)
        np.testing.assert_allclose(total_momentum(result), p_before)


# ===========================================================================
# 5) RANDFAELLE
# ===========================================================================
class TestEdgeCases(unittest.TestCase):

    def test_empty_list_returns_empty(self):
        self.assertEqual(len(Collisions.handle([], DT)), 0)

    def test_single_body_unchanged(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [1, 2, 3], 1.0)
        result = Collisions.handle([b1], DT)
        self.assertEqual(len(result), 1)
        self.assertIn(b1, result)

    def test_no_collision_keeps_all_objects(self):
        b1 = make_body("Earth", 1.0, [0, 0, 0], [0, 0, 0], 1.0)
        b2 = make_body("Moon", 1.0, [100, 0, 0], [0, 0, 0], 1.0)
        result = Collisions.handle([b1, b2], DT)
        self.assertIn(b1, result)
        self.assertIn(b2, result)


if __name__ == "__main__":
    unittest.main()
