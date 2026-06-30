"""Analyzes which launch speeds and angles hit the Moon.
uses sweep_fast() for the notebook and sweep() for testing.
all values in SI units (m/s, degrees, meters).
"""

import math

import numpy as np

import constants
from scenarios import create_cannon_shot, create_earth_moon
from simulation import Simulation
from integrator import Verlet


# slow reference path (not used by the notebook, only by the tests)

def min_distance_to_moon(history):
    #Returns the minimum distance the projectile reached the Moon.

    best = math.inf
    for snapshot in history:
        projectile = moon = None
        for body in snapshot["bodies"]:
            if body["name"] == "Projectile":
                projectile = body
            elif body["name"] == "Moon":
                moon = body
        if projectile is None or moon is None:
            continue
        distance = np.linalg.norm(
            np.asarray(projectile["position"]) - np.asarray(moon["position"])
        )
        if distance < best:
            best = distance
    return best


def _is_moon_hit(history):
    # after a merge the body is named "Moon_Projectile"
    # so just look for one of the components
    for snapshot in history:
        for body in snapshot["bodies"]:
            name = body["name"]
            if "Projectile" in name and "Moon" in name:
                return True
    return False


def sweep(speeds, angles, duration=3.5, integrator=None, dt=None):
    # runs one simulation per (speed, angle) pair
    # returns 2-D arrays of hits and minimum distances
    # the notebook uses sweep_fast() instead.
    speeds = np.asarray(speeds, dtype=float)
    angles = np.asarray(angles, dtype=float)
    integrator_cls = type(integrator) if integrator is not None else Verlet

    hits = np.zeros((len(speeds), len(angles)), dtype=bool)
    min_dist = np.full((len(speeds), len(angles)), math.inf, dtype=float)

    for i, speed in enumerate(speeds):
        for j, angle in enumerate(angles):
            bodies, config = create_cannon_shot(float(speed), float(angle))
            if dt is not None:
                config = {**config, "time_step": dt}
            sim = Simulation(bodies, config, duration=duration,
                             integrator=integrator_cls())
            sim.simulate()
            hits[i, j] = _is_moon_hit(sim.history)
            min_dist[i, j] = min_distance_to_moon(sim.history)

    return {"speeds": speeds, "angles": angles, "hits": hits, "min_dist": min_dist}


# Precomputes Earth-Moon orbit once,
# then vectorizes all (speed, angle) projectiles through it with numpy
# same physics as sweep(), much faster.

def _earth_moon_trajectory(duration, dt):
    # run the Earth-Moon orbit once and keep both positions at every step
    bodies, _ = create_earth_moon()
    earth, moon = bodies
    integrator = Verlet()
    n_steps = round(duration * 24 * 60 * 60 / dt)

    earth_xyz = np.empty((n_steps + 1, 3))
    moon_xyz = np.empty((n_steps + 1, 3))
    earth_xyz[0] = earth.position
    moon_xyz[0] = moon.position
    for k in range(1, n_steps + 1):
        integrator.step(bodies, dt)
        earth_xyz[k] = earth.position
        moon_xyz[k] = moon.position
    return earth_xyz, moon_xyz


def _propagate_projectiles(pos0, vel0, earth_xyz, moon_xyz, dt):
    # verlet-steps all projectiles through precomputed Earth-Moon field
    # projectiles freeze on Moon hit or Earth crash
    # returns closest Moon distance and hit status per projectile.
    GM_earth = Constants.G * Constants.EARTH_MASS
    GM_moon = Constants.G * Constants.MOON_MASS
    r_moon_hit = Constants.MOON_RADIUS + Constants.PROJECTILE_RADIUS
    r_earth_hit = Constants.EARTH_RADIUS + Constants.PROJECTILE_RADIUS

    pos = pos0.astype(float).copy()
    pos_prev = pos - vel0 * dt          # backwards seed, like Verlet's first step with Mini-Euler
    active = np.ones(len(pos), dtype=bool)
    moon_hit = np.zeros(len(pos), dtype=bool)
    min_moon = np.full(len(pos), math.inf)

    n = earth_xyz.shape[0]
    for t in range(n):
        to_moon = pos - moon_xyz[t]
        d_moon = np.linalg.norm(to_moon, axis=1)
        np.minimum(min_moon, np.where(active, d_moon, math.inf), out=min_moon)

        newly_hit = active & (d_moon <= r_moon_hit)
        moon_hit |= newly_hit
        to_earth = pos - earth_xyz[t]
        d_earth = np.linalg.norm(to_earth, axis=1)
        crashed = active & (d_earth <= r_earth_hit)
        active &= ~(newly_hit | crashed)

        if t == n - 1 or not active.any():
            break

        accel = (-GM_earth * to_earth / d_earth[:, None] ** 3
                 - GM_moon * to_moon / d_moon[:, None] ** 3)
        pos_new = 2.0 * pos - pos_prev + accel * dt * dt
        moving = active[:, None]
        pos_prev = np.where(moving, pos, pos_prev)
        pos = np.where(moving, pos_new, pos)

    return min_moon, moon_hit


def sweep_fast(speeds, angles, duration=3.5, dt=None):
    # fast vectorized sweep (what the notebook calls).
    # same grid output as sweep().
    speeds = np.asarray(speeds, dtype=float)
    angles = np.asarray(angles, dtype=float)
    if dt is None:
        dt = Constants.DEFAULT_CANNON_TIME_STEP

    earth_xyz, moon_xyz = _earth_moon_trajectory(duration, dt)

    # one projectile per (speed, angle), same launch as create_cannon_shot
    start_r = Constants.EARTH_RADIUS + Constants.PROJECTILE_RADIUS + 1000.0
    speed_grid = np.repeat(speeds, len(angles))          # (S*A,)
    angle_grid = np.tile(angles, len(speeds))            # (S*A,)
    angle_rad = np.radians(angle_grid)

    pos0 = np.zeros((speed_grid.size, 3))
    vel0 = np.zeros((speed_grid.size, 3))
    pos0[:, 0] = start_r * np.cos(angle_rad)
    pos0[:, 1] = start_r * np.sin(angle_rad)
    vel0[:, 0] = speed_grid * np.cos(angle_rad)
    vel0[:, 1] = speed_grid * np.sin(angle_rad)

    min_moon, moon_hit = _propagate_projectiles(pos0, vel0, earth_xyz, moon_xyz, dt)

    shape = (len(speeds), len(angles))
    return {"speeds": speeds, "angles": angles,
            "hits": moon_hit.reshape(shape), "min_dist": min_moon.reshape(shape)}


def plot_corridor_heatmap(grid, ax=None):
    # plots a heatmap: speed (x-axis) vs angle (y-axis),
    # colored by closest Moon distance
    # red line marks Moon surface (hit boundary),
    # dashed white line marks escape velocity.
    from matplotlib import pyplot as plt
    from matplotlib.colors import LogNorm

    speeds_kms = grid["speeds"] / 1000.0
    angles = grid["angles"]
    min_dist = grid["min_dist"].T   # grid is [speed, angle]; transpose -> x=speed, y=angle
    hit_radius = Constants.MOON_RADIUS + Constants.PROJECTILE_RADIUS

    if ax is None:
        _, ax = plt.subplots()

    mesh = ax.pcolormesh(speeds_kms, angles, min_dist,
                         norm=LogNorm(), cmap="viridis_r", shading="nearest")
    ax.figure.colorbar(mesh, ax=ax, label="closest distance to Moon [m]")

    # outline the cells that actually reach the Moon
    if (min_dist <= hit_radius).any() and (min_dist > hit_radius).any():
        ax.contour(speeds_kms, angles, min_dist, levels=[hit_radius],
                   colors="red", linewidths=1.5)

    # the wall: below escape velocity nothing gets away from Earth
    v_esc = Constants.EARTH_ESCAPE_VELOCITY / 1000.0
    if speeds_kms.min() <= v_esc <= speeds_kms.max():
        ax.axvline(v_esc, color="white", linestyle="--", linewidth=1)
        ax.text(v_esc, angles.max(), f" v_esc ≈ {v_esc:.2f} km/s",
                color="white", va="top", ha="left", fontsize=8)

    ax.set_xlabel("Launch speed [km/s]")
    ax.set_ylabel("Lead angle [deg]")
    ax.set_title("Hit corridor (red = Moon surface)")
    return ax