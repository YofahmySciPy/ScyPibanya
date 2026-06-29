import numpy as np


class Body:


    name: str
    mass: float
    radius: float
    position: np.ndarray
    velocity: np.ndarray
    position_previous: np.ndarray
    acceleration: np.ndarray


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


        self.position_previous = None
        self.acceleration = np.array([0.0, 0.0, 0.0])



    def diameter(self):
        return 2.0 * self.radius

    def distance_to(self, other_body):
        return np.linalg.norm(other_body.position - self.position)

    def distance_vector_to(self, other_body):
       return other_body.position - self.position

    def is_touching(self, other_body):
        return self.distance_to(other_body) <= self.radius + other_body.radius

    def momentum(self):
        return self.mass * self.velocity

    def kinetic_energy(self):
        return 0.5 * self.mass * np.linalg.norm(self.velocity)**2



    def __repr__(self):
        return f"Body('{self.name}', mass={self.mass:.3e} kg, position={self.position})"
