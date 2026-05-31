### Body (`src/Body.py`)
A `Body` is one object in space (Earth, Moon or projectile).

**Properties:** `name`, `mass`, `radius`, `position`, `velocity`,`position_previous`,`acceleration`

**Methods:** `diameter()`, `distance_to(other)`, `distance_vector_to(other)`,`is_touching(other)`, `momentum()`.

**Create a body** with the constructor, for example:

    erde = Body("Earth", EARTH_MASS, EARTH_RADIUS, [0, 0, 0], [0, 0, 0])





### Constants (`src/Constants.py`)
All values in **SI units** (meters, kg, seconds):
`G`,
the Earth (mass, radius),
the Moon (mass, radius, distance, orbital speed and period),
derived check values,
time units, and the cannon parameters for task 2.1 (speeds + angles).