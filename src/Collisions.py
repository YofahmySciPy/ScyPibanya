import numpy as np

from body import Body


class Collisions:

    @staticmethod
    def handle(bodies, dt):

        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                b1 = bodies[i]
                b2 = bodies[j]

                distance = np.linalg.norm(b1.position - b2.position)

                if distance <= b1.radius + b2.radius:
                    new_body = Collisions.merge(b1, b2, dt)

                    # remove the two old bodies, add the new one,
                    # and start from the beginning till nothing changes
                    new_list = [b for k, b in enumerate(bodies)
                                if k != i and k != j]
                    new_list.append(new_body)
                    return Collisions.handle(new_list, dt)

        return bodies

    @staticmethod
    def merge(b1, b2, dt):

        name_new = b1.name + "_" + b2.name

        m_new = b1.mass + b2.mass

        v_new = (b1.mass * b1.velocity + b2.mass * b2.velocity) / m_new

        r_new = (b1.mass * b1.position + b2.mass * b2.position) / m_new

        radius_new = (b1.radius**3 + b2.radius**3) ** (1 / 3)

        new_body = Body(
            name=name_new,
            mass=m_new,
            position=r_new,
            velocity=v_new,
            radius=radius_new,
        )

        # set position_previous for verlet calculations
        new_body.position_previous = r_new - v_new * dt

        return new_body