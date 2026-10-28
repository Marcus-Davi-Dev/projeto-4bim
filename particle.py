import pygame
import math

class Particle:
    vacuum_constant = 9*10**9 # 9.10e9
    @classmethod
    def calculate_radius(cls, exp):
        return abs(exp)*4
    def __init__(self, x: float, y: float, charge: float, exp: int):
        self.x = x
        self.y = y
        self.chargeMantissa = charge
        self.chargeExponent = exp
        self.radius = abs(exp)*4
    def __repr__(self):
        return f"(x={self.x}, y={self.y}, chargeMantissa={self.chargeMantissa}, exp={self.chargeExponent}, radius={self.radius})"

    def render(self, surface: pygame.Surface, offset: tuple[int, int] | tuple[float, float] | list[int] | list[float]):
        if self.chargeMantissa > 0:
            color = (0, 0, 255)
        elif self.chargeMantissa == 0:
            color = (80, 80, 80)
        else:
            color = (255, 0, 0)
        pygame.draw.circle(surface, color, (self.x - offset[0], self.y - offset[1]), self.radius)
    
    def potential(self, Q: Particle):
        distance = math.sqrt((Q.x - self.x)**2 + (Q.y - self.y)**2)
        return Particle.vacuum_constant * 10**Q.chargeExponent*Q.chargeMantissa/distance
    
    def potential_energy(self, Q: Particle):
        distance = math.sqrt((Q.x - self.x)**2 + (Q.y - self.y)**2)
        return Particle.vacuum_constant * (10**Q.chargeExponent*Q.chargeMantissa * 10**self.chargeExponent*self.chargeMantissa)/distance

    def eletrostatic_force(self, Q: Particle):
        distance = math.sqrt((Q.x - self.x)**2 + (Q.y - self.y)**2)
        return Particle.vacuum_constant * (10**Q.chargeExponent*Q.chargeMantissa * 10**self.chargeExponent*self.chargeMantissa)/(distance**2)
    
    def eletric_field(self, Q: Particle):
        distance = math.sqrt((Q.x - self.x)**2 + (Q.y - self.y)**2)
        return Particle.vacuum_constant * (10**Q.chargeExponent*Q.chargeMantissa * 10**self.chargeExponent*self.chargeMantissa)/(distance**2)