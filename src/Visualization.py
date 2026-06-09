from typing import Literal

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib.widgets import Slider

import Constants


def extract_trajectories(history):
    if not history:
        raise ValueError("history must contain at least one snapshot")

    names = [body_snapshot["name"] for body_snapshot in history[0]["bodies"]]
    times = np.array([snapshot["t"] for snapshot in history])
    positions = {
        name: np.array([snapshot["bodies"][index]["position"] for snapshot in history])
        for index, name in enumerate(names)
    }
    return times, positions


def _planar_extent(bodies, positions):
    xy = np.vstack([positions[body.name][:, :2] for body in bodies])
    span_x = xy[:, 0].max() - xy[:, 0].min()
    span_y = xy[:, 1].max() - xy[:, 1].min()
    return max(span_x, span_y)


def auto_body_scale(bodies, positions, visible_fraction=0.05):
    if not bodies:
        raise ValueError("bodies must not be empty")

    max_radius = max(body.radius for body in bodies)
    if max_radius <= 0:
        raise ValueError("all bodies must have a positive radius")

    extent = _planar_extent(bodies, positions)
    if extent <= 0:
        return 1.0
    return (visible_fraction * extent) / max_radius


def _resolve_body_scale(body_scale: Literal["auto"] | float, bodies, positions):
    if body_scale == "auto":
        return auto_body_scale(bodies, positions)
    if body_scale <= 0:
        raise ValueError(f"body_scale must be positive, got {body_scale}")
    return float(body_scale)


def _body_colors(bodies):
    palette = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    return {body.name: palette[index % len(palette)] for index, body in enumerate(bodies)}


def _display_radius(true_display_radius, span, min_display_fraction):
    return max(true_display_radius, min_display_fraction * span)


def plot_system(bodies, history, body_scale: Literal["auto"] | float = "auto",
                unit=Constants.KM, unit_label="km",
                show_trajectories=True, min_display_fraction=0.012, ax=None, title=None):
    _, positions = extract_trajectories(history)
    body_scale = _resolve_body_scale(body_scale, bodies, positions)
    span = _planar_extent(bodies, positions) / unit
    colors = _body_colors(bodies)

    if ax is None:
        _, ax = plt.subplots(figsize=(7, 7))

    for body in bodies:
        color = colors[body.name]
        xy = positions[body.name][:, :2] / unit
        if show_trajectories:
            ax.plot(xy[:, 0], xy[:, 1], linewidth=1, alpha=0.7, color=color,
                    label=f"{body.name} (Bahn)")
        display_radius = _display_radius(body.radius * body_scale / unit, span, min_display_fraction)
        ax.add_patch(Circle(xy[-1], display_radius, zorder=3, facecolor=color,
                            edgecolor="black", linewidth=0.6, label=body.name))
        ax.annotate(body.name, xy[-1], xytext=(4, 4), textcoords="offset points")

    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel(f"x [{unit_label}]")
    ax.set_ylabel(f"y [{unit_label}]")
    ax.set_title(title or f"Bahnen in der X/Y-Ebene (Körper {body_scale:.3g}-fach vergrößert)")
    ax.legend(loc="upper right", fontsize="small")
    return ax


def animate_system(bodies, history, body_scale: Literal["auto"] | float = "auto",
                    unit=Constants.KM, unit_label="km",
                    frame_step=1, trail_length=200, min_display_fraction=0.012,
                    interval=30, figsize=(5, 5), dpi=80, title=None):
    if frame_step <= 0:
        raise ValueError(f"frame_step must be a positive integer, got {frame_step}")

    times, positions = extract_trajectories(history)
    frame_indices = list(range(0, len(times), frame_step))

    body_scale = _resolve_body_scale(body_scale, bodies, positions)
    colors = _body_colors(bodies)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    all_xy = np.vstack([positions[body.name][:, :2] for body in bodies]) / unit
    span = max(all_xy[:, 0].max() - all_xy[:, 0].min(),
               all_xy[:, 1].max() - all_xy[:, 1].min())
    margin = 0.1 * span if span > 0 else 1.0
    ax.set_xlim(all_xy[:, 0].min() - margin, all_xy[:, 0].max() + margin)
    ax.set_ylim(all_xy[:, 1].min() - margin, all_xy[:, 1].max() + margin)
    ax.set_aspect("equal")
    ax.set_xlabel(f"x [{unit_label}]")
    ax.set_ylabel(f"y [{unit_label}]")
    ax.set_title(title or f"Simulation (Körper {body_scale:.3g}-fach vergrößert)")

    trails = {}
    markers = {}
    for body in bodies:
        color = colors[body.name]
        trail_line, = ax.plot([], [], linewidth=1, alpha=0.5, color=color)
        trails[body.name] = trail_line
        true_radius = body.radius * body_scale / unit
        display_radius = _display_radius(true_radius, span, min_display_fraction)
        circle = Circle((0.0, 0.0), display_radius, zorder=3, facecolor=color,
                        edgecolor="black", linewidth=0.6, label=body.name)
        ax.add_patch(circle)
        markers[body.name] = circle
    ax.legend(loc="upper right", fontsize="small")
    time_label = ax.text(0.02, 0.97, "", transform=ax.transAxes, va="top")

    def update(frame_number):
        index = frame_indices[frame_number]
        trail_start = max(0, index - trail_length) if trail_length > 0 else index
        for body in bodies:
            xy = positions[body.name][:, :2] / unit
            markers[body.name].center = xy[index]
            if trail_length > 0:
                trails[body.name].set_data(xy[trail_start:index + 1, 0], xy[trail_start:index + 1, 1])
        time_label.set_text(f"t = {times[index] / Constants.DAY:.2f} d")
        return [*markers.values(), *trails.values(), time_label]

    return animation.FuncAnimation(fig, update, frames=len(frame_indices),
                                   interval=interval, blit=True)


def interactive_system(bodies, history, unit=Constants.KM, unit_label="km",
                        min_display_fraction=0.012, title=None):
    _, positions = extract_trajectories(history)
    initial_scale = auto_body_scale(bodies, positions)
    span = _planar_extent(bodies, positions) / unit
    colors = _body_colors(bodies)

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.subplots_adjust(bottom=0.2)

    circles = {}
    for body in bodies:
        color = colors[body.name]
        xy = positions[body.name][:, :2] / unit
        ax.plot(xy[:, 0], xy[:, 1], linewidth=1, alpha=0.7, color=color,
                label=f"{body.name} (Bahn)")
        display_radius = _display_radius(body.radius * initial_scale / unit, span, min_display_fraction)
        circle = Circle(xy[-1], display_radius, zorder=3, facecolor=color,
                        edgecolor="black", linewidth=0.6, label=body.name)
        ax.add_patch(circle)
        circles[body] = circle

    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel(f"x [{unit_label}]")
    ax.set_ylabel(f"y [{unit_label}]")
    ax.set_title(title or "Bahnen in der X/Y-Ebene")
    ax.legend(loc="upper right", fontsize="small")

    slider_axes = fig.add_axes((0.2, 0.06, 0.6, 0.03))
    scale_slider = Slider(slider_axes, "Vergrößerung der Körper",
                          valmin=0.1 * initial_scale, valmax=25.0 * initial_scale,
                          valinit=initial_scale)

    def on_scale_changed(scale):
        for body, circle in circles.items():
            true_radius = body.radius * scale / unit
            circle.set_radius(_display_radius(true_radius, span, min_display_fraction))
        fig.canvas.draw_idle()

    scale_slider.on_changed(on_scale_changed)
    return fig, scale_slider


def plot_distance_over_time(history, name_a, name_b, collision_distance=None,
                             unit=Constants.KM, unit_label="km", ax=None, title=None):
    times, positions = extract_trajectories(history)
    if name_a not in positions:
        raise KeyError(f"no body named '{name_a}' in this history")
    if name_b not in positions:
        raise KeyError(f"no body named '{name_b}' in this history")

    distance = np.linalg.norm(positions[name_a] - positions[name_b], axis=1)

    if ax is None:
        _, ax = plt.subplots(figsize=(8, 4))

    ax.plot(times / Constants.DAY, distance / unit, label=f"Abstand {name_a} - {name_b}")
    if collision_distance is not None:
        ax.axhline(collision_distance / unit, color="red", linestyle="--",
                   label="Kontaktabstand (Kollision)")

    ax.set_xlabel("Zeit [Tage]")
    ax.set_ylabel(f"Abstand [{unit_label}]")
    ax.set_title(title or f"Abstand {name_a} - {name_b} über die Zeit")
    ax.legend(loc="best", fontsize="small")
    return ax


def _frame_step_for(history, target_frames=150):
    return max(1, len(history) // target_frames)


def _demo_earth_moon():
    from Simulation import Simulation
    from Scenarios import create_earth_moon

    bodies, config = create_earth_moon()
    sim = Simulation(bodies, config)
    orbit_steps = int(Constants.MOON_ORBITAL_PERIOD / config["time_step"])
    sim.simulate(orbit_steps)
    print(f"Erde-Mond-System: simulierte Zeit {sim.t / Constants.DAY:.2f} Tage "
          f"({len(sim.history)} Zeitschritte aufgezeichnet)")

    orbit_animation = animate_system(bodies, sim.history, frame_step=_frame_step_for(sim.history),
                                      trail_length=len(sim.history),
                                      title="Der Mond umkreist die Erde (ein voller Orbit)")
    plt.show()


def _simulate_cannon_shot(speed, lead_angle_deg, time_limit_hours=30.0):
    from Simulation import Simulation
    from Scenarios import create_cannon_shot

    bodies, config = create_cannon_shot(speed, lead_angle_deg)
    sim = Simulation(bodies, config)
    earth, moon, projectile = bodies
    fly_past_distance = 1.3 * Constants.EARTH_MOON_DISTANCE
    max_steps = int(time_limit_hours * Constants.HOUR / config["time_step"])

    for _ in range(max_steps):
        sim.step()
        if projectile.is_touching(earth) or projectile.is_touching(moon):
            break
        if projectile.distance_to(earth) > fly_past_distance:
            break
    return sim


def _describe_cannon_outcome(sim):
    earth, moon, projectile = sim.bodies
    if projectile.is_touching(moon):
        return "TREFFER - das Geschoss erreicht den Mond"
    if projectile.is_touching(earth):
        return "faellt zurueck zur Erde"
    if projectile.distance_to(earth) > 1.3 * Constants.EARTH_MOON_DISTANCE:
        return "fliegt am Mond vorbei"
    return "Zeitlimit erreicht (noch unterwegs)"


def _demo_cannon_scenarios():
    import itertools

    print("Kanonenschuss-Szenarien (Aufgabe 2.1): alle 9 vorgeschlagenen Kombinationen")
    for speed, lead_angle in itertools.product(Constants.CANNON_SPEEDS, Constants.CANNON_LEAD_ANGLES):
        sim = _simulate_cannon_shot(speed, lead_angle)
        outcome = _describe_cannon_outcome(sim)
        print(f"  v0 = {speed / Constants.KM:.0f} km/s, Vorhaltewinkel = {lead_angle:.0f} deg "
              f"-> {outcome} (Flugzeit: {sim.t / Constants.HOUR:.2f} h)")

        scenario_animation = animate_system(
            sim.bodies, sim.history,
            frame_step=_frame_step_for(sim.history, target_frames=80),
            trail_length=150,
            title=f"Kanonenschuss: v0 = {speed / Constants.KM:.0f} km/s, "
                  f"Vorhaltewinkel = {lead_angle:.0f} deg -> {outcome}")
        plt.show()


def _estimate_lead_angle(launch_speed, num_samples=200_000):
    radii = np.linspace(Constants.EARTH_RADIUS, Constants.EARTH_MOON_DISTANCE, num_samples)
    speed_squared = (launch_speed**2
                     - 2 * Constants.G * Constants.EARTH_MASS * (1.0 / Constants.EARTH_RADIUS - 1.0 / radii))
    travel_time = np.trapezoid(1.0 / np.sqrt(speed_squared), radii)
    angular_speed = 2 * np.pi / Constants.MOON_ORBITAL_PERIOD
    return np.degrees(angular_speed * travel_time) % 360.0


def _demo_cannon_hit():
    launch_speed = Constants.CANNON_SPEEDS[2]
    estimated_angle = _estimate_lead_angle(launch_speed)
    print(f"Geschaetzter Vorhaltewinkel fuer v0 = {launch_speed / Constants.KM:.0f} km/s: "
          f"{estimated_angle:.2f} deg")

    hit_lead_angle = 11.5
    sim = _simulate_cannon_shot(launch_speed, hit_lead_angle)
    _, moon, projectile = sim.bodies
    outcome = _describe_cannon_outcome(sim)
    print(f"v0 = {launch_speed / Constants.KM:.0f} km/s, Vorhaltewinkel = {hit_lead_angle:.1f} deg "
          f"-> {outcome} (Flugzeit bis zum Einschlag: {sim.t / Constants.HOUR:.2f} h, "
          f"Schaetzung war {estimated_angle:.2f} deg)")

    hit_animation = animate_system(sim.bodies, sim.history,
                                    frame_step=_frame_step_for(sim.history, target_frames=100),
                                    trail_length=200,
                                    title=f"Treffer: v0 = {launch_speed / Constants.KM:.0f} km/s, "
                                          f"Vorhaltewinkel = {hit_lead_angle:.1f} deg")
    plt.show()

    plot_distance_over_time(sim.history, "Projectile", "Moon",
                            collision_distance=projectile.radius + moon.radius,
                            title=f"Abstand Geschoss-Mond (v0 = {launch_speed / Constants.KM:.0f} km/s, "
                                  f"Vorhaltewinkel = {hit_lead_angle:.1f} deg)")
    plt.show()


def main():
    _demo_earth_moon()
    _demo_cannon_scenarios()
    _demo_cannon_hit()


if __name__ == "__main__":
    main()