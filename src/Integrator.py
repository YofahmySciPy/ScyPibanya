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
        print(f"bodies: {len(bodies)}")
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                if i != j:

                    p1 = bodies[i]
                    p2 = bodies[j]
                    direction = Body.distance_vector_to(p1,p2)
                    r = np.linalg.norm(direction)
                    print(f"i={i}, j={j}, r={r}")
                    if r > 1e-12:
                        direction_norm = direction / r

                        F = G * p1.mass * p2.mass / r**2
                        print(f"i={i}, j={j}, direction={direction}, r={r}, F={F}")

                        a1 = F / p1.mass
                        a2 = F / p2.mass

                        bodies[i].acceleration += a1 * direction_norm
                        bodies[j].acceleration -= a2 * direction_norm






class  Verlet(Integrator):
    def step(self, bodies, dt):
        """
        REFERENCE CODE, DOES NOT WORK(https://www.algorithm-archive.org/contents/verlet_integration/verlet_integration.html):
            function verlet(pos::Float64, acc::Float64, dt::Float64)
            prev_pos = pos
            time = 0.0

            while (pos > 0)
                time += dt
                temp_pos = pos
                pos = pos * 2 - prev_pos + acc * dt * dt
                prev_pos = temp_pos
            end

            return time
        """
        prev_pos = bodies.position_previous.copy()
        temp_pos = bodies.position.copy()

        bodies.position = bodies.position * 2 - prev_pos + bodies.acceleration.copy() * dt * dt
        bodies.position_previous = temp_pos




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