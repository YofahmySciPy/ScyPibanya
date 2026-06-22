from Integrator import Verlet, Euler
from Scenarios import create_earth_moon, create_cannon_shot
from Collisions import Collisions

class Simulation:

    def __init__(self, bodies, config, duration, integrator=None):
        self.bodies = bodies
        self.dt = config["time_step"]
        self.duration = duration*24*60*60 # Convert duration from days to seconds
        self.steps = int(self.duration/self.dt)
        self.integrator = integrator if integrator is not None else Verlet()
        self.t = 0.0
        self.history = []
        self._save_snapshot()

    @staticmethod
    def build_simulation(cannon, duration, integrator=None, cannon_angle=None, cannonball_speed=None):
        if cannon:
            if cannon_angle is None or cannonball_speed is None:
                raise ValueError("To start the cannon shot, provide the cannon angle and the cannonball speed")
            bodies, config = create_cannon_shot(cannonball_speed, cannon_angle)
        else:
            bodies, config = create_earth_moon()
        return Simulation(bodies, config, duration=duration, integrator=integrator)
    
    def step(self):
        self.integrator.step(self.bodies, self.dt)
        self.bodies = Collisions.handle(self.bodies, self.dt)
        self.t += self.dt
        self._save_snapshot()

    def _save_snapshot(self):
        snapshot = {
            "t": self.t,
            "bodies": [
                {
                "name": b.name,
                "mass": b.mass,
                "radius": b.radius,
                "position": b.position.copy(),
                "velocity": b.velocity.copy()
                }
                for b in self.bodies
            ]
        }
        self.history.append(snapshot)

    def simulate(self):
        for i in range(self.steps):
            self.step()