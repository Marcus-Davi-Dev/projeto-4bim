import pygame
import sys
import math
from particle import Particle
import custom_font
import json
import constants.colors as colors
# import WHI

def to_rad(deg: float) -> float:
    return deg/180*math.pi

# screen
screen = pygame.display.set_mode((800, 600))
GRID_SIZE = 50

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

def draw_grid(surface: pygame.Surface, squares_size: int, color):
    """Draws the grid in which the particles will be. It does NOT render it, you have to use pygame.display.flip() or .update() manually."""
    for i in range(int(surface.width/squares_size)): # colunas
        pygame.draw.line(surface, color, (i*squares_size, 0), (i*squares_size, surface.height))

    for i in range(int(surface.width/squares_size)): # linhas
        pygame.draw.line(surface, color, (0, i*squares_size), (surface.width, i*squares_size))

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
    screen.fill(colors.WHITE)
    
    draw_grid(screen, GRID_SIZE, colors.GRAY)
    
    if len(particles) == 2:
        text_surface = font.render(f"Ptl: {particles[0].potential_energy(particles[1])}", 14, colors.RED)
        screen.blit(text_surface, (5, 5))
    else:
        text_surface = font.render(f"ABCDEFGHIJKLMNOPQRTSUVWXYZ", 16, colors.RED)
        screen.blit(text_surface, (5, 5))
        text_surface2 = font.render(f"abcdefghijklmnopqrstuvwxyz1234567890", 16, colors.RED)
        screen.blit(text_surface2, (5, 37))
    
    for p in particles:
        p.render(screen)

    
    # print(particles)

    pygame.display.flip()