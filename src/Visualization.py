import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib.widgets import RadioButtons, TextBox, Button

import Constants
from Integrator import Verlet, Euler
from Simulation import Simulation
from Scenarios import create_earth_moon, create_cannon_shot

MIN_DISPLAY_FRACTION = 0.012


def extract_trajectories(history):
    """Liest aus der Simulationshistorie für jeden Körper die Positionen über die Zeit aus."""
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
    """Berechnet die größte Ausdehnung aller Körper in der X/Y-Ebene."""
    xy = np.vstack([positions[body.name][:, :2] for body in bodies])
    return max(xy[:, 0].max() - xy[:, 0].min(), xy[:, 1].max() - xy[:, 1].min())


def auto_body_scale(bodies, positions, visible_fraction=0.05):
    """Berechnet einen Vergrößerungsfaktor, sodass der größte Körper sichtbar bleibt."""
    max_radius = max(body.radius for body in bodies)
    extent = _planar_extent(bodies, positions)
    return (visible_fraction * extent) / max_radius


def animate_system(bodies, history, unit=Constants.KM, unit_label="km",
                    frame_step=1, trail_length=200, interval=30, figsize=(5, 5), dpi=80, title=None):
    """Erstellt eine Animation, die die Simulation Schritt für Schritt abspielt."""
    times, positions = extract_trajectories(history)
    frame_indices = list(range(0, len(times), frame_step))

    scale = auto_body_scale(bodies, positions)
    palette = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    all_xy = np.vstack([positions[body.name][:, :2] for body in bodies]) / unit
    span = max(all_xy[:, 0].max() - all_xy[:, 0].min(), all_xy[:, 1].max() - all_xy[:, 1].min())
    margin = 0.1 * span if span > 0 else 1.0
    ax.set_xlim(all_xy[:, 0].min() - margin, all_xy[:, 0].max() + margin)
    ax.set_ylim(all_xy[:, 1].min() - margin, all_xy[:, 1].max() + margin)
    ax.set_aspect("equal")
    ax.set_xlabel(f"x [{unit_label}]")
    ax.set_ylabel(f"y [{unit_label}]")
    ax.set_title(title or "Simulation")

    trails = {}
    markers = {}
    for index, body in enumerate(bodies):
        color = palette[index % len(palette)]
        trails[body.name], = ax.plot([], [], linewidth=1, alpha=0.5, color=color)
        # Mindestgröße MIN_DISPLAY_FRACTION * span, damit auch sehr kleine Körper (z.B. das Geschoss) sichtbar bleiben
        display_radius = max(body.radius * scale / unit, MIN_DISPLAY_FRACTION * span)
        circle = Circle((0.0, 0.0), display_radius, zorder=3,
                        facecolor=color, edgecolor="black", linewidth=0.6, label=body.name)
        ax.add_patch(circle)
        markers[body.name] = circle
    ax.legend(loc="upper right", fontsize="small")
    time_label = ax.text(0.02, 0.97, "", transform=ax.transAxes, va="top")

    def update(frame_number):
        # Bewegt Marker und Bahnspuren zum jeweils nächsten aufgezeichneten Zeitschritt
        index = frame_indices[frame_number]
        trail_start = max(0, index - trail_length)
        for body in bodies:
            xy = positions[body.name][:, :2] / unit
            markers[body.name].center = xy[index]
            trails[body.name].set_data(xy[trail_start:index + 1, 0], xy[trail_start:index + 1, 1])
        time_label.set_text(f"t = {times[index] / Constants.DAY:.2f} d")
        return [*markers.values(), *trails.values(), time_label]

    return animation.FuncAnimation(fig, update, frames=len(frame_indices), interval=interval, blit=True)


def plot_distance_over_time(history, name_a, name_b, collision_distance=None,
                             unit=Constants.KM, unit_label="km", ax=None, title=None):
    """Zeichnet den Abstand zwischen zwei Körpern über die Zeit."""
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


# ---------------------------------------------------------------------------
# Demo: Zeigt zuerst das Erde-Mond-System
# (Aufgabe 1) und öffnet dann ein Fenster, in dem Integrator, Geschwindigkeit und
# Vorhaltewinkel für einen Kanonenschuss (Aufgabe 2.1) eingestellt werden können.
# Jeder Klick auf "Schuss starten" simuliert und animiert einen weiteren Schuss.
# ---------------------------------------------------------------------------

# hält Referenzen auf alle Animationen, damit sie nicht vom Garbage Collector entfernt werden
_active_animations = []


def _frame_step_for(history, target_frames=150):
    """Wählt frame_step so, dass eine Animation über `history` ungefähr `target_frames` Frames hat."""
    return max(1, len(history) // target_frames)


def _show_earth_moon_orbit(orbits=1):
    """Aufgabe 1: simuliert `orbits` Mondumläufe und zeigt sie als Animation mit vollständiger Bahnspur."""
    bodies, config = create_earth_moon()
    earth, _moon = bodies
    sim = Simulation(bodies, config, Verlet())
    orbit_steps = int(orbits * Constants.MOON_ORBITAL_PERIOD / config["time_step"])
    sim.simulate(orbit_steps)

    orbit_label = "ein voller Orbit" if orbits == 1 else f"{orbits} Orbits"
    _active_animations.append(animate_system(bodies, sim.history, frame_step=_frame_step_for(sim.history),
                                               trail_length=len(sim.history),
                                               title=f"Der Mond umkreist die Erde ({orbit_label})"))
    # Zweite Animation, gezoomt auf die kleine Eigenbewegung der Erde um den Schwerpunkt
    _active_animations.append(animate_system([earth], sim.history, frame_step=_frame_step_for(sim.history),
                                               trail_length=len(sim.history),
                                               title="Eigenbewegung der Erde um den Schwerpunkt"))
    plt.show(block=False)


def _run_cannon_shot(integrator, speed, lead_angle):
    """Aufgabe 2.1: simuliert einen Kanonenschuss und zeigt ihn als Animation sowie den Abstand zum Mond über die Zeit."""
    bodies, config = create_cannon_shot(speed, lead_angle)
    sim = Simulation(bodies, config, integrator)
    earth, moon, projectile = bodies

    # bis zu 30 Stunden simulieren, früher abbrechen sobald das Geschoss Erde oder Mond berührt
    max_steps = int(30 * Constants.HOUR / config["time_step"])
    for _ in range(max_steps):
        sim.step()
        if projectile.is_touching(earth) or projectile.is_touching(moon):
            break

    title = (f"Kanonenschuss: v0 = {speed:.0f} m/s, Vorhaltewinkel = {lead_angle:.1f} deg, "
             f"{type(integrator).__name__} (Flugzeit {sim.t / Constants.HOUR:.2f} h)")
    _active_animations.append(animate_system(sim.bodies, sim.history,
                                               frame_step=_frame_step_for(sim.history, target_frames=100),
                                               trail_length=len(sim.history), title=title))
    plot_distance_over_time(sim.history, "Projectile", "Moon",
                            collision_distance=projectile.radius + moon.radius,
                            title="Abstand Geschoss-Mond")
    plt.show(block=False)


def _open_cannon_shot_launcher():
    """Öffnet ein Fenster zur Auswahl von Integrator, Geschwindigkeit und Vorhaltewinkel; jeder Klick auf
    "Schuss starten" simuliert und animiert einen weiteren Kanonenschuss mit den eingestellten Werten."""
    fig = plt.figure(figsize=(4, 3))
    fig.suptitle("Kanonenschuss")

    integrator_radio = RadioButtons(fig.add_axes((0.1, 0.45, 0.35, 0.4)), ("Verlet", "Euler"))
    speed_box = TextBox(fig.add_axes((0.55, 0.7, 0.35, 0.1)), "v0 [m/s]", initial="12000")
    angle_box = TextBox(fig.add_axes((0.55, 0.5, 0.35, 0.1)), "Winkel [deg]", initial="0")
    shoot_button = Button(fig.add_axes((0.55, 0.25, 0.35, 0.15)), "Schuss starten")

    def on_shoot_clicked(_event):
        # liest die aktuellen Einstellungen aus und startet damit einen weiteren Kanonenschuss
        integrator = Verlet() if integrator_radio.value_selected == "Verlet" else Euler()
        _run_cannon_shot(integrator, float(speed_box.text), float(angle_box.text))

    shoot_button.on_clicked(on_shoot_clicked)
    plt.show()


def main():
    """Zeigt das Erde-Mond-System und öffnet danach den Kanonenschuss-Launcher für beliebig viele Schüsse."""
    _show_earth_moon_orbit(2)
    _open_cannon_shot_launcher()


if __name__ == "__main__":
    main()
