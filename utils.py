import math

def to_rad(deg: float) -> float:
    return deg/180*math.pi

def to_deg(rad: float) -> float:
    return rad*180/math.pi

def distance(pos1: tuple[float, float], pos2: tuple[float, float]):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)