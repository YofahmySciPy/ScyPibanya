from Integrator import Verlet, Euler

class Simulation:

    def __init__(self, bodies, config, integrator=None):
        self.bodies = bodies
        self.dt = config["time_step"]
        self.integrator = integrator if integrator is not None else Verlet()
        self.t = 0.0
        self.history = []
        self._save_snapshot()
    
    def step(self):
        self.integrator.step(self.bodies, self.dt)
        # Check here for collisions, when implemented
        self.t += self.dt
        self._save_snapshot()

    def _save_snapshot(self):
        snapshot = {
            "t": self.t,
            "bodies": [
                {
                "name": b.name,
                "mass": b.mass,
                "position": b.position.copy(),
                "velocity": b.velocity.copy()
                }
                for b in self.bodies
            ]
        }
        self.history.append(snapshot)

    def simulate(self, steps):
        for i in range(steps):
            self.step()