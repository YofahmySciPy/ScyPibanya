import numpy as np


class Body:


    name: str
    mass: float
    radius: float
    position: np.ndarray
    velocity: np.ndarray
    previous: np.ndarray


    def __init__(self, name, mass, radius, position, velocity):

        if mass <= 0:
            raise ValueError(f"mass must be positive, got {mass}")
        if radius <= 0:
            raise ValueError(f"radius must be positive, got {radius}")

        self.name = name
        self.mass = mass
        self.radius = radius

        # in numpy array umwandeln
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)

        # muss immer Achsen
        if self.position.shape != (3,):
            raise ValueError(f"position must have 3 values [x, y, z], got {position}")
        if self.velocity.shape != (3,):
            raise ValueError(f"velocity must have 3 values [vx, vy, vz], got {velocity}")


        self.previous = None



    def diameter(self):
        return 2.0 * self.radius

    def distance_to(self, other_body):
        return np.linalg.norm(self.position - other_body.position)

    def is_touching(self, other_body):
        return self.distance_to(other_body) <= self.radius + other_body.radius

    def momentum(self):
        return self.mass * self.velocity

    def __repr__(self):
        return f"Body('{self.name}', mass={self.mass:.3e} kg, position={self.position})"
