from IPython.display import HTML, display
import ipywidgets as widgets
from matplotlib import pyplot as plt

from integrator import Euler, Verlet
from simulation import Simulation
from visualization import Visualization


def map_integrator(name):
    if name == "Verlet":
        return Verlet()
    elif name == "Euler":
        return Euler()
    else:
        raise ValueError(f"Input: {name}, Expected: Verlet or Euler")


def run(cannon, integrator_name, duration, angle, speed, size_factor):
    integrator = map_integrator(integrator_name)
    sim = Simulation.build_simulation(cannon, duration, integrator=integrator,
                                      cannonball_angle=angle, cannonball_speed=speed)
    sim.simulate()
    viz = Visualization()
    viz.animate(sim.history, size_factor=size_factor)
    return viz


def render(viz):
    html = viz.anim.to_jshtml()
    plt.close(viz.fig)
    return HTML(html)


def build_panel():
    cannonball_checkbox = widgets.Checkbox(value=False, description="Kanonenschuss aktivieren")
    cannonball_speed = widgets.BoundedFloatText(min=5, max=25, value=12.3, step=0.1,
                                                description="Geschwindigkeit (km/s)",
                                                style={"description_width": "150px"})
    cannonball_angle = widgets.BoundedFloatText(min=0, max=30, value=10, step=0.1,
                                                description="Winkel (°)")
    duration = widgets.BoundedFloatText(min=1, max=500, step=1, value=30, description="Dauer (Tage)")
    integrator = widgets.Dropdown(options=["Verlet", "Euler"], value="Verlet", description="Integrator")
    scale = widgets.BoundedFloatText(min=1000, max=50000, step=1000, value=15000, description="Körpergröße")

    cannon_row = widgets.HBox([cannonball_angle, cannonball_speed])
    general_row = widgets.HBox([duration, integrator])

    loading_html = widgets.HTML(value='<i class="fa fa-spinner fa-spin fa-2x"></i> Berechnung läuft...')

    def disable_cannon_widgets(change):
        is_active = change["new"]
        cannonball_angle.disabled = not is_active
        cannonball_speed.disabled = not is_active
        if is_active:
            duration.max = 30
            duration.value = 5
        else:
            duration.max = 240
            duration.value = 30

    cannonball_checkbox.observe(disable_cannon_widgets, names="value")
    disable_cannon_widgets({"new": False})

    output = widgets.Output()

    def on_start_clicked(b):
        with output:
            output.clear_output()
            display(loading_html)
            try:
                viz = run(cannonball_checkbox.value, integrator.value, duration.value,
                          cannonball_angle.value, cannonball_speed.value * 1000, scale.value)
                html = render(viz)
                output.clear_output()
                display(html)
            except Exception as e:
                print(f"Fehler: {e}")

    start_button = widgets.Button(button_style="info", description="Simulation Starten")
    start_button.on_click(on_start_clicked)

    panel = widgets.VBox([cannonball_checkbox, cannon_row, general_row, scale, start_button, output])

    refs = {
        "cannonball_checkbox": cannonball_checkbox,
        "cannonball_speed": cannonball_speed,
        "cannonball_angle": cannonball_angle,
        "duration": duration,
        "integrator": integrator,
        "scale": scale,
        "start_button": start_button,
        "output": output,
    }

    return panel, refs