import numpy as np
from abc import ABC, abstractmethod
from Constants import G
from Body import Body



class Integrator(ABC):
    @abstractmethod
    def step(self, bodies, dt):
        pass


    def calculate_acceleration(self, bodies):
        for i in bodies:
            i.acceleration = np.zeros(3)
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):

                p1 = bodies[i]
                p2 = bodies[j]
                direction = Body.distance_vector_to(p1,p2)
                r = np.linalg.norm(direction)
                if r > 1e-12:
                    direction_norm = direction / r

                    F = G * p1.mass * p2.mass / r**2

                    a1 = F / p1.mass
                    a2 = F / p2.mass

                    bodies[i].acceleration += a1 * direction_norm
                    bodies[j].acceleration -= a2 * direction_norm

    def potential_energy(self, bodies):
        E_pot = 0.0
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                r = np.linalg.norm(bodies[j].position - bodies[i].position)
                if r > 1e-12:
                    E_pot += -G * bodies[i].mass * bodies[j].mass / r
        return E_pot






class  Verlet(Integrator):
    def step(self, bodies, dt):

        Integrator.calculate_acceleration(self, bodies)

        # Mini-Euler nur beim allerersten Schritt:
        # setzt position_previous rückwärts, ohne position zu bewegen
        for body in bodies:
            if body.position_previous is None:
                body.position_previous = body.position - body.velocity * dt

        for i in range(len(bodies)):
            prev_pos = bodies[i].position_previous.copy()
            temp_pos = bodies[i].position.copy()

            bodies[i].position = bodies[i].position * 2 - prev_pos + bodies[i].acceleration.copy() * dt * dt
            bodies[i].position_previous = temp_pos




class Euler(Integrator):

    def step(self, bodies, dt):
        # explicit euler with big errors
        Integrator.calculate_acceleration(self, bodies)

        for body in bodies:
            temp_vel = body.velocity.copy()

            body.velocity += body.acceleration * dt
            body.position += temp_vel * dt