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




### Integrator (`src/Integrator.py`)

The `Integrator` module provides numerical integration methods for simulating N-body gravitational systems. 
It contains an abstract base class `Integrator` with different concrete implementations for time-stepping algorithms.

#### Core Concepts

**Gravitational Acceleration Calculation**

The `calculate_acceleration()` method computes the gravitational forces between all body pairs using Newton's law of universal gravitation:

```
F = G * m₁ * m₂ / r²
a = F / m
```

Since forces are symmetric (F₁₂ = -F₂₁), the method only loops through unique pairs `i < j`, 
applying equal and opposite accelerations:
- Body i receives acceleration in the direction of body j
- Body j receives acceleration in the opposite direction

All accelerations are reset to zero at the start of each calculation.

```python
import numpy as np

def calculate_acceleration(self, bodies):
    # Reset all accelerations
    for body in bodies:
        body.acceleration = np.zeros(3)

    # N-body gravitational computation (O(N²))
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            # Compute force and apply to both bodies symmetrically
            pass
```

**Potential Energy**

The `potential_energy()` method computes the total gravitational potential energy of the system:

```
E_pot = -G * Σ(m₁ * m₂ / r)  for all pairs i < j
```

This is useful for energy conservation checks.

#### Integration Methods

**Verlet Integration** (`Verlet` class)

The Verlet method is a position-based integration algorithm that is more stable than simple Euler integration, 
especially for oscillatory systems. Position Verlet does not explicitly track velocity; instead:

1. Initialize `position_previous` on the first step:
   ```
   position_previous = position - velocity * dt
   ```

2. Update position using the Verlet formula:
   ```
   position_new = 2 * position - position_previous + acceleration * dt²
   position_previous = position
   ```

3. Velocity can be recovered implicitly (if needed) as:
   ```
   velocity ≈ (position_new - position_previous) / (2 * dt)
   ```

**Usage Example:**

```python
from Integrator import Verlet
from Body import Body
from Constants import G

bodies = [
    Body("Earth", 5.972e24, 6.371e6, [0, 0, 0], [0, 30000, 0]),
    Body("Moon", 7.342e22, 1.737e6, [3.844e8, 0, 0], [0, 1022, 0])
]

verlet = Verlet()
dt = 1000  # 1000 seconds per step
num_steps = 1000000  # simulation time steps

for step in range(num_steps):
    verlet.step(bodies, dt)
    energy = verlet.potential_energy(bodies)
    # log or visualize state
```

**Euler Integration** (`Euler` class)

This repository implements the explicit (forward) Euler integrator in `src/Integrator.py`. 
The implementation follows the classical explicit update:

Formulas (explicit / forward Euler):

1. Velocity update:
```
v_{n+1} = v_n + a_n * dt
```
2. Position update (explicit uses the old velocity):
```
x_{n+1} = x_n + v_n * dt
```

Implementation note (matches current code): the integrator computes accelerations first, 
then for each body copies the current velocity, updates the velocity using the acceleration, 
and advances the position with the saved (old) velocity. 
This exact pattern avoids using the just-updated velocity for the position step.

Example (matches `src/Integrator.py`):

```python
def step(self, bodies, dt):
    # compute accelerations (in-place)
    self.calculate_acceleration(bodies)

    # explicit Euler: update velocity, step position using old velocity
    for body in bodies:
        v_old = body.velocity.copy()
        body.velocity += body.acceleration * dt
        body.position += v_old * dt
```

Pros/Cons
- Pros: trivial to implement and fast per step; useful for quick prototypes and debugging.
- Cons: first-order accurate and unstable for many orbital problems — expect significant energy drift unless dt is very small.

Testing & validation
- Re-run the two-body circular orbit comparison used for Verlet. Expect Euler to show rapid energy drift unless dt is reduced strongly.
- Add unit tests that ensure the integrator runs without exceptions for a 2‑body system and preserves expected array shapes and types.




#### Constants

All calculations use the gravitational constant from `Constants.py`:
```
G = 6.67430e-11  # m³ kg⁻¹ s⁻²
```

All positions, velocities, and masses are in **SI units** (meters, m/s, kg).

#### Performance Notes

- Acceleration calculation is **O(N²)**, suitable for systems with up to ~1000 bodies.
- Verlet is symplectic (energy-preserving in the long term) and recommended for orbital mechanics.
- No collision detection is currently integrated; bodies can pass through each other.
