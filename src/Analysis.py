"""
Analysis tools for research question 2.1:
Which combination of launch angle and speed makes the cannon
projectile hit the Moon?

This module only MEASURES the existing simulation. It does not
modify the simulation, scenarios, collisions, or the timestep.
"""

import numpy as np

from Simulation import Simulation
from Integrator import Verlet
import Constants


def min_distance_to_moon(speed, angle_deg, duration_days):
    """
    Build a cannon-shot simulation with the given speed (m/s),
    angle (degrees), and duration (days). Run it.

    Return a dict with:
        "min_distance"   : minimum Projectile<->Moon distance [m]
        "time"           : time [s] at which that minimum occurred
        "collision"      : True if the Projectile name disappeared
                           (merged into a compound body)
        "collision_time" : time [s] of that merge (or None)
        "collision_with" : name of the merged body, e.g.
                           "Moon_Projectile" or "Earth_Projectile"
                           (or None)
        "hit_moon"       : True if the Projectile merged into a body
                           whose name contains both "Moon" and
                           "Projectile" (a real Moon impact). An
                           Earth merge does NOT count.
    """
    sim = Simulation.build_simulation(
        cannon=True,
        duration=duration_days,
        integrator=Verlet(),
        cannonball_angle=angle_deg,
        cannonball_speed=speed,
    )
    sim.simulate()

    min_dist = float("inf")
    min_t = None
    collision = False
    collision_time = None
    collision_with = None
    hit_moon = False

    for snap in sim.history:
        t = snap["t"]
        bodies = snap["bodies"]
        by_name = {b["name"]: b for b in bodies}

        proj = by_name.get("Projectile")
        moon = by_name.get("Moon")

        # The Projectile name vanishes once it merges into a compound
        # body (collision). Record the first frame where that happens.
        if proj is None and not collision:
            collision = True
            collision_time = t
            collision_with = next(
                (b["name"] for b in bodies if "Projectile" in b["name"]),
                None,
            )
            # A real Moon impact: the merged body carries both names.
            # An "Earth_Projectile" merge must NOT count as a Moon hit.
            if collision_with is not None and "Moon" in collision_with:
                hit_moon = True

        # Only a "live" Projectile and a "live" Moon give a meaningful
        # separation. After a merge either name may be gone.
        if proj is None or moon is None:
            continue

        d = float(np.linalg.norm(
            np.asarray(proj["position"], dtype=float)
            - np.asarray(moon["position"], dtype=float)
        ))
        if d < min_dist:
            min_dist = d
            min_t = t

    return {
        "min_distance": min_dist,
        "time": min_t,
        "collision": collision,
        "collision_time": collision_time,
        "collision_with": collision_with,
        "hit_moon": hit_moon,
    }


def sweep(speeds, angles, duration_days):
    """
    For each (speed, angle) pair, call min_distance_to_moon and print
    a readable table:

        speed | angle | min_distance_km | hit?

    "hit" is yes when the Projectile actually merges into the Moon
    (the authoritative collision signal), not merely when the sampled
    minimum distance dips below Moon_radius + Projectile_radius.
    """
    hit_threshold = Constants.MOON_RADIUS + Constants.PROJECTILE_RADIUS

    print(f"Hit threshold = Moon_radius + Projectile_radius "
          f"= {hit_threshold:,.0f} m = {hit_threshold / 1000.0:,.1f} km")
    print("hit? = yes when the Projectile merges into the Moon "
          "(Moon_Projectile)\n")

    header = (f"{'speed (m/s)':>11} | {'angle (deg)':>11} | "
              f"{'min_dist (km)':>14} | {'hit?':>4}")
    print(header)
    print("-" * len(header))

    for speed in speeds:
        for angle in angles:
            res = min_distance_to_moon(speed, angle, duration_days)
            min_km = res["min_distance"] / 1000.0
            hit = res["hit_moon"]
            hit_str = "YES" if hit else "no"

            note = ""
            if res["collision"]:
                note = (f"   merge -> {res['collision_with']} "
                        f"@ t={res['collision_time']:,.0f}s")

            print(f"{speed:>11.0f} | {angle:>11.0f} | "
                  f"{min_km:>14.1f} | {hit_str:>4}{note}")


def _report_thresholds_and_tunneling():
    """Print the hit threshold and a one-step tunneling sanity check."""
    moon_r = Constants.MOON_RADIUS
    proj_r = Constants.PROJECTILE_RADIUS
    dt = Constants.DEFAULT_CANNON_TIME_STEP

    fastest = 12000.0  # m/s, the top of the 2.1 launch-speed range
    step_travel = fastest * dt

    print("=== Thresholds (from Constants) ===")
    print(f"Moon radius        = {moon_r:,.0f} m = {moon_r / 1000:,.2f} km")
    print(f"Projectile radius  = {proj_r:,.0f} m = {proj_r / 1000:,.4f} km")
    print(f"Hit threshold      = {(moon_r + proj_r) / 1000:,.2f} km\n")

    print("=== Timestep tunneling check @ 12000 m/s ===")
    print(f"DEFAULT_CANNON_TIME_STEP = {dt:.0f} s")
    print(f"Distance per step  = 12000 * {dt:.0f} = {step_travel:,.0f} m "
          f"= {step_travel / 1000:,.1f} km")
    print(f"Moon radius        = {moon_r / 1000:,.1f} km, "
          f"Moon diameter = {2 * moon_r / 1000:,.1f} km")
    print(f"step_travel / Moon_radius   = {step_travel / moon_r:.3f}")
    print(f"step_travel / Moon_diameter = {step_travel / (2 * moon_r):.3f}")
    if step_travel < moon_r:
        print("OK: one step is shorter than the Moon radius -> "
              "the projectile cannot tunnel past the Moon.\n")
    else:
        print("WARNING: one step exceeds the Moon radius -> "
              "tunneling is possible.\n")


if __name__ == "__main__":
    _report_thresholds_and_tunneling()

    print("=== Sweep (duration = 30 days) ===")
    sweep(
        speeds=[9000, 11000, 12000, 15000],
        angles=[0, 10, 20, 30, 40, 50],
        duration_days=30,
    )
