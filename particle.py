import pygame
import math

class Particle:
    vacuum_constant = 9*10**9 # 9.10e9
    def __init__(self, x: float, y: float, charge: float, exp: int):
        self.x = x
        self.y = y
        self.chargeMantissa = charge
        self.chargeExponent = exp
    def __repr__(self):
        return f"(x={self.x}, y={self.y}, chargeMantissa={self.chargeMantissa}, exp:={self.chargeExponent})"

    def render(self, surface: pygame.Surface):

        if self.chargeMantissa > 0:
            color = (0, 0, 255)
        elif self.chargeMantissa == 0:
            color = (80, 80, 80)
        else:
            color = (255, 0, 0)
        pygame.draw.circle(surface, color, (self.x, self.y), abs(self.chargeExponent)*4)
    
    def potential(self, Q: Particle):
        distance = math.sqrt((Q.x - self.x)**2 + (Q.y - self.y)**2)
        return Particle.vacuum_constant * 10**Q.chargeExponent*Q.chargeMantissa/distance
    
    def potential_energy(self, Q: Particle):
        distance = math.sqrt((Q.x - self.x)**2 + (Q.y - self.y)**2)
        return Particle.vacuum_constant * (10**Q.chargeExponent*Q.chargeMantissa * 10**self.chargeExponent*self.chargeMantissa)/distance