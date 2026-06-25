from Integrator import Verlet, Euler
from Simulation import Simulation
from Visualization import Visualization
from matplotlib import pyplot as plt
from IPython.display import HTML


def map_integrator(name) :
    if name == "Verlet" :
        return Verlet()
    elif name == "Euler" :
        return Euler()
    else :
        raise ValueError(f"Input: {name}, Expected: Verlet or Euler" )

def run(cannon, integrator_name, duration, angle, speed, size_factor):
    integrator = map_integrator(integrator_name)
    sim = Simulation.build_simulation(cannon, duration,integrator= integrator,cannon_angle= angle, cannonball_speed= speed)
    sim.simulate()
    viz = Visualization()
    viz.animate(sim.history, size_factor=size_factor)
    return viz

def render (viz):
    html = viz.anim.to_jshtml()
    plt.close(viz.fig)
    return HTML(html)
