import math
from Body import Body
import Constants


def create_earth_moon():
    earth = Body("Earth",Constants.EARTH_MASS,Constants.EARTH_RADIUS,[0,0,0],[0,0,0])
    moon = Body("Moon",Constants.MOON_MASS,Constants.MOON_RADIUS,[Constants.MOON_START_X,0,0],[0,Constants.MOON_CIRCULAR_VELOCITY,0])
    config = {"time_step": Constants.DEFAULT_EARTH_MOON_TIME_STEP}
    return [earth,moon],config

def create_cannon_shot(speed,angle_deg):
    angle_rad = math.radians(angle_deg)
    earth = Body("Earth",Constants.EARTH_MASS,Constants.EARTH_RADIUS,[0,0,0],[0,0,0])
    moon = Body("Moon",Constants.MOON_MASS,Constants.MOON_RADIUS,[Constants.MOON_START_X,0,0],[0,Constants.MOON_CIRCULAR_VELOCITY,0])
    pos_x = Constants.EARTH_RADIUS * math.cos(angle_rad)
    pos_y = Constants.EARTH_RADIUS * math.sin(angle_rad)
    vel_x = speed * math.cos(angle_rad)
    vel_y = speed * math.sin(angle_rad)
    projectile = Body("Projectile",Constants.PROJECTILE_MASS,Constants.PROJECTILE_RADIUS,[pos_x,pos_y,0],[vel_x,vel_y,0])
    config = {"time_step": Constants.DEFAULT_CANNON_TIME_STEP}
    return [earth,moon,projectile],config