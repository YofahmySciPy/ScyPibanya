"""

UNIT CONVENTION (SI)
    Length      in meters        [m]
    Mass        in kilograms      [kg]
    Time        in seconds        [s]
    Velocity    in [m/s]
    Angle       internally in degrees [deg]  (convert to rad only when computing)

"""

import math

# ---------------------------------------------------------------------------
# 1. Fundamental constant
# ---------------------------------------------------------------------------

G = 6.67430e-11


# ---------------------------------------------------------------------------
# 2. Earth
# ---------------------------------------------------------------------------

EARTH_MASS   = 5.972e24
EARTH_RADIUS = 6.371e6


# ---------------------------------------------------------------------------
# 3. Moon
# ---------------------------------------------------------------------------

MOON_MASS   = 7.346e22
MOON_RADIUS = 1.7374e6


# Orbit of the Moon around Earth (center to center):
EARTH_MOON_DISTANCE = 3.844e8
MOON_ORBITAL_SPEED  = 1022.0
MOON_ORBITAL_PERIOD = 27.322 * 86400.0




# Initial state for the simulation (Earth sits in the origin 0/0/0):
#   the Moon starts on the +X axis and moves in the +Y direction,
#   so it orbits inside the X/Y plane
MOON_START_X  = EARTH_MOON_DISTANCE   # start position on the X axis [m]
MOON_START_VY = MOON_ORBITAL_SPEED    # start velocity in the Y direction [m/s]


# ---------------------------------------------------------------------------
# 4. Derived reference values (to validate the simulation)
# ---------------------------------------------------------------------------

# Earth escape velocity:  v = sqrt(2 * G * M / R)   -> approx. 11,186 m/s
EARTH_ESCAPE_VELOCITY = math.sqrt(2.0 * G * EARTH_MASS / EARTH_RADIUS)

# Theoretical circular orbital velocity of the Moon:  v = sqrt(G * M / r)
# -> approx. 1018 m/s, should match MOON_ORBITAL_SPEED (1022) -> sanity check
MOON_CIRCULAR_VELOCITY = math.sqrt(G * EARTH_MASS / EARTH_MOON_DISTANCE)


# ---------------------------------------------------------------------------
# 5. Time units (for readable time steps and time-lapse)
# ---------------------------------------------------------------------------

SECOND = 1.0
MINUTE = 60.0 * SECOND
HOUR   = 60.0 * MINUTE
DAY    = 24.0 * HOUR             # 86,400 s

DEFAULT_CANNON_TIME_STEP = MINUTE         # default time step [s] = 1 minute per step
DEFAULT_EARTH_MOON_TIME_STEP = HOUR


# ---------------------------------------------------------------------------
# 6. Length unit (only for display conversion)
# ---------------------------------------------------------------------------

KM = 1000.0                      # 1 kilometer = 1000 meters


# ---------------------------------------------------------------------------
# 7. Task 2.1 - The Gun Club and the Columbiad
# ---------------------------------------------------------------------------

# Given launch velocities [m/s] (PDF: 7, 9, 12 km/s):
CANNON_SPEEDS = (7.0 * KM, 9.0 * KM, 12.0 * KM)   # = (7000, 9000, 12000) m/s

# Lead angles [degrees]: where the gun points relative to the Moon
#   0 deg  = exactly at the Moon
#   15 deg = 15 degrees ahead of the Moon's position
#   30 deg = 30 degrees ahead of the Moon's position
CANNON_LEAD_ANGLES = (0.0, 15.0, 30.0)

# Projectile properties (free to choose - tiny compared to Earth/Moon):
PROJECTILE_MASS   = 1.0e4        # [kg]  = 10 tons (example value)
PROJECTILE_RADIUS = 1.0          # [m]   (point mass, only for collision test)