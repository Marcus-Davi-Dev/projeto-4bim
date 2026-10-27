import pygame
import sys
import math
from particle import Particle
import custom_font
import json
import constants.colors as colors
from utils import *

# screen
screen = pygame.display.set_mode((800, 600))
GRID_SIZE = 50

# the list of particles
particles: list[Particle] = []

# flags to track whether the user has clicked once or just kept the mouse firing inputs
mousePressedButtons = [False, False, False]

def onclick(ev: pygame.event.Event):
    if len(particles) >= 2:
        return
    
    if len(particles) == 1 and distance(ev.pos, (particles[0].x, particles[0].y)) < particles[0].radius+Particle.calculate_radius(-6):
        return

    charge = -20 if ev.button == 1 else 20
    particles.append(Particle(ev.pos[0], ev.pos[1], charge, -6))

def draw_grid(surface: pygame.Surface, squares_size: int, color):
    """Draws the grid in which the particles will be. It does NOT render it, you have to use pygame.display.flip() or .update() manually."""
    for i in range(int(surface.get_width()/squares_size)): # colunas
        pygame.draw.line(surface, color, (i*squares_size, 0), (i*squares_size, surface.get_height()))

    for i in range(int(surface.get_width()/squares_size)): # linhas
        pygame.draw.line(surface, color, (0, i*squares_size), (surface.get_width(), i*squares_size))

font = custom_font.CustomFont()
custom_font.init()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button >= 1 and event.button <= 3:
                mousePressedButtons[event.button-1] = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button >= 1 and event.button <= 3:
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
        potential_energy = font.render(f"Ptl energy: {particles[0].potential_energy(particles[1])}", 14, colors.RED)
        screen.blit(potential_energy, (5, 5))
        
        potential = font.render(f"Ptl: {particles[0].potential(particles[1])}", 14, colors.RED)
        screen.blit(potential, (5, 19))
        
        force = font.render(f"Eletrostatic force: {particles[0].eletrostatic_force(particles[1])}", 14, colors.RED)
        screen.blit(force, (5, 34))
        
        field = font.render(f"Eletric field: {particles[0].eletric_field(particles[1])}", 14, colors.RED)
        screen.blit(field, (5, 48))
        
        cateto_oposto = abs(particles[0].y - particles[1].y)
        hipotenusa = math.sqrt((particles[0].x - particles[1].x)**2 + (particles[0].y - particles[1].y)**2)
        # cateto_adjacente = abs(particles[0].x - particles[1].x)
        
        angle = to_deg(math.asin(cateto_oposto/hipotenusa))
        
        if particles[0].x < particles[1].x and particles[0].y < particles[1].y: # quadrante inferior esquerdo
            angle *= -1
        elif particles[0].x < particles[1].x and particles[0].y > particles[1].y: # quadrante superior esquerdo
            pass # nesse caso tá de boa
        elif particles[0].x > particles[1].x and particles[0].y > particles[1].y: # quadrante superior direito
            angle = 180 - angle
        elif particles[0].x > particles[1].x and particles[0].y > particles[1].y: # quadrante inferior direito
            angle += 180
        
        font_size = 16
        text = font.render(f"{angle}", font_size, colors.GREEN)
        rotated_text = pygame.transform.rotate(text, angle)
        
        screen.blit(rotated_text, (
            max(particles[0].x, particles[1].x) - abs(particles[0].x - particles[1].x)/2 - rotated_text.get_width()/2,
            max(particles[0].y, particles[1].y) - abs(particles[0].y - particles[1].y)/2 - rotated_text.get_height()/2)
        )
        
        pygame.draw.line(screen, colors.YELLOW, (particles[0].x, particles[0].y), (particles[1].x, particles[1].y), 4)
    else:
        potential_energy = font.render(f"Ptl energy: 0", 14, colors.RED)
        screen.blit(potential_energy, (5, 5))
        
        potential = font.render(f"Ptl: 0", 14, colors.RED)
        screen.blit(potential, (5, 19))
        
        force = font.render(f"Eletrostatic force: 0", 14, colors.RED)
        screen.blit(force, (5, 34))
        
        field = font.render(f"Eletric field: 0", 14, colors.RED)
        screen.blit(field, (5, 48))
    
    for p in particles:
        p.render(screen)

    
    # print(particles)

    pygame.display.flip()