from abc import ABC, abstractmethod

class Integrator(ABC):
    @abstractmethod
    def step(self, bodies, dt):
        pass


    @abstractmethod
    def calculate_acceleration(self, bodies):
        pass

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
        prev_pos = bodies.prev_pos.copy()
        temp_pos = bodies.pos.copy()

        bodies.pos = bodies.pos * 2 - prev_pos + bodies.acc.copy() * dt * dt
        bodies.prev_pos = temp_pos

        pass

class Euler(Integrator):

    def step(self, bodies, dt):
        temp_pos = bodies.pos.copy()
        temp_vel = bodies.vel.copy()
        temp_acc = 0

        bodies.vel += temp_acc
        bodies.pos += temp_vel



        pass

