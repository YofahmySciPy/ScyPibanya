class Body():

    def __init__(self, name, mass, radius, velocity, position):
        if mass < 0:
            self.mass = 0
        if radius < 0:
            self.radius = 0

        self.name = name
        self.mass = mass # kg
        self.radius = radius # m
        self.diameter = 2 * self.radius # m
        self.position = position # m
        self.velocity = velocity # m / s
        self.momentum = self.mass * self.velocity # kg * m / s

    def __repr__(self):
        return (
            f"Body(name='{self.name}', "
            f"mass={self.mass} kg, "
            f"radius={self.radius:.3e} m, "
            f"pos={self.position} m, "
            f"vel={self.velocity} m/s, "
            f"mom={self.momentum} kg*m/s)"
        )
