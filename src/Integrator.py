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






class  Verlet(Integrator):
    def step(self, bodies, dt):

        Integrator.calculate_acceleration(self, bodies)

        # mini-Euler step to set the previous position
        # TODO: ----TEST----
        for body in bodies:
            body.position_previous = body.position.copy()
            body.velocity += body.acceleration * dt
            body.position += body.velocity * dt

        # TODO: ----TEST----
        for i in range(len(bodies)):
            prev_pos = bodies[i].position_previous.copy()
            temp_pos = bodies[i].position.copy()

            # TODO: add formula to readme
            bodies[i].position = bodies[i].position * 2 - prev_pos + bodies[i].acceleration.copy() * dt * dt
            bodies[i].position_previous = temp_pos




class Euler(Integrator):

    def step(self, bodies, dt):
        #temp_pos = bodies.pos.copy()
        temp_vel = bodies.vel.copy()
        temp_acc = 0

        bodies.vel += temp_acc
        bodies.pos += temp_vel



        pass

    def calculate_acceleration(self, bodies):
        pass