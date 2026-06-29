import math

from body import Body
import constants


def create_earth_moon():
    earth = Body("Earth",constants.EARTH_MASS,constants.EARTH_RADIUS,[0,0,0],[0,0,0])
    moon = Body("Moon",constants.MOON_MASS,constants.MOON_RADIUS,[constants.MOON_START_X,0,0],[0,constants.MOON_CIRCULAR_VELOCITY,0])
    config = {"time_step": constants.DEFAULT_EARTH_MOON_TIME_STEP}
    return [earth,moon],config

def create_cannon_shot(speed,angle_deg):
    angle_rad = math.radians(angle_deg)
    earth = Body("Earth",constants.EARTH_MASS,constants.EARTH_RADIUS,[0,0,0],[0,0,0])
    moon = Body("Moon",constants.MOON_MASS,constants.MOON_RADIUS,[constants.MOON_START_X,0,0],[0,constants.MOON_CIRCULAR_VELOCITY,0])
    start_r = constants.EARTH_RADIUS + constants.PROJECTILE_RADIUS + 1000.0 
    pos_x = start_r * math.cos(angle_rad)
    pos_y = start_r * math.sin(angle_rad)
    vel_x = speed * math.cos(angle_rad)
    vel_y = speed * math.sin(angle_rad)
    projectile = Body("Projectile",constants.PROJECTILE_MASS,constants.PROJECTILE_RADIUS,[pos_x,pos_y,0],[vel_x,vel_y,0])
    config = {"time_step": constants.DEFAULT_CANNON_TIME_STEP}
    return [earth,moon,projectile],config

def create_67():
    earth = Body("Earth",constants.EARTH_MASS,constants.EARTH_RADIUS,[0,0,0],[0,0,0])
    moon = Body("Moon",constants.MOON_MASS,constants.MOON_RADIUS,[constants.MOON_START_X,0,0],[0,constants.MOON_CIRCULAR_VELOCITY / 2,0])
    config = {"time_step": constants.DEFAULT_EARTH_MOON_TIME_STEP}
    return [earth,moon],config