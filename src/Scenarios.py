from .Body import Body
from . import Constants


def create_earth_moon():
    earth = Body("Earth",Constants.EARTH_MASS,Constants.EARTH_RADIUS,[0,0,0],[0,0,0])
    moon = Body("Moon",Constants.MOON_MASS,Constants.MOON_RADIUS,[Constants.MOON_START_X,0,0],[0,Constants.MOON_CIRCULAR_VELOCITY,0])
    config = {"time_step": Constants.DEFAULT_TIME_STEP, "duration": Constants.MOON_ORBITAL_PERIOD}
    return [earth,moon],config

