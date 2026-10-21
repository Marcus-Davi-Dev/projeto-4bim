import pygame
import sys
import math
from particle import Particle
import custom_font
import json

def to_rad(deg: float) -> float:
    return deg/180*math.pi

# screen
screen = pygame.display.set_mode((1800, 1200))

# colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# for the spinning circles (sadly, deprecated, can be removed)
# degs = 0
# ORBIT = 40

# the list of particles
particles: list[Particle] = []

# flags to track whether the user has clicked once or just kept the mouse firing inputs
mousePressedButtons = [False, False, False]

def onclick(ev: pygame.event.Event):
    if len(particles) >= 2:
        return

    charge = -20 if ev.button == 1 else 20
    particles.append(Particle(ev.pos[0], ev.pos[1], charge, -6))

font = custom_font.CustomFont()
custom_font.init()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # print(event.button)
            mousePressedButtons[event.button-1] = True
        if event.type == pygame.MOUSEBUTTONUP:
            onclick(event)
            mousePressedButtons[event.button-1] = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                particles = []
            if event.key == pygame.K_l:
                with open("bitmap.json") as file:
                    map = file.read()
                    font.update_bitmap(json.loads(map))
    screen.fill(WHITE)
    
    if len(particles) == 2:
        text_surface = font.render(f"Ptl: {particles[0].potential_energy(particles[1])}", 14, BLACK)
        screen.blit(text_surface, (5, 5))
    else:
        text_surface = font.render(f"Bom dia meus caros amigos e amigas.", 14, BLACK)
        screen.blit(text_surface, (5, 5))
    
    for p in particles:
        p.render(screen)
    
    # print(particles)

    pygame.display.flip()