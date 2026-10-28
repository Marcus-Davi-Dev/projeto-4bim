import pygame
import sys
import math
from particle import Particle
import custom_font
import json
import constants.colors as colors
from utils import *

# screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

GRID_SIZE = 50
world_offset = [0.0, 0.0]

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
    particles.append(Particle(ev.pos[0]+world_offset[0], ev.pos[1]+world_offset[1], charge, -6))

def draw_grid(surface: pygame.Surface, squares_size: int, color: tuple[int, int, int] | tuple[int, int, int, int], offset: tuple[int, int] | tuple[float, float] | list[int] | list[float] = (0, 0)):
    """Draws the grid in which the particles will be. It does NOT render it, you have to use pygame.display.flip() or .update() manually."""
    for i in range(int(surface.get_width()/squares_size) + 1): # colunas
        pygame.draw.line(surface, color, (i*squares_size - offset[0]%squares_size, 0), (i*squares_size - offset[0]%squares_size, surface.get_height()))

    for i in range(int(surface.get_height()/squares_size) + 1): # linhas
        pygame.draw.line(surface, color, (0, i*squares_size - offset[1]%squares_size), (surface.get_width(), i*squares_size - offset[1]%squares_size))

font = custom_font.CustomFont()
custom_font.init()

clock = pygame.time.Clock()

running = True
while running:
    delta = clock.tick()
    pressed_keys = pygame.key.get_pressed()
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
    
    offset_increase = 1 * delta / 7
    
    if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
        offset_increase *= 2.5
            
    if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
        world_offset[0] -= offset_increase
    if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
        world_offset[0] += offset_increase
    if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
        world_offset[1] -= offset_increase
    if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
        world_offset[1] += offset_increase
    screen.fill(colors.WHITE)
    
    draw_grid(screen, GRID_SIZE, colors.GRAY, world_offset)
    
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
        
        offsetX = 0
        offsetY = 0
        
        if particles[0].x < particles[1].x and particles[0].y < particles[1].y: # quadrante inferior esquerdo
            angle *= -1
        elif particles[0].x < particles[1].x and particles[0].y > particles[1].y: # quadrante superior esquerdo
            pass # nesse caso tá de boa
        elif particles[0].x > particles[1].x and particles[0].y > particles[1].y: # quadrante superior direito
            angle = 180 - angle
            offsetX -= 16
        elif particles[0].x > particles[1].x and particles[0].y > particles[1].y: # quadrante inferior direito
            angle += 180
        
        font_size = 16
        text = font.render(f"{angle}", font_size, colors.GREEN)
        rotated_text = pygame.transform.rotate(text, angle)
        
        screen.blit(rotated_text, (
            max(particles[0].x, particles[1].x) - abs(particles[0].x - particles[1].x)/2 - rotated_text.get_width()/2 + offsetX - world_offset[0],
            max(particles[0].y, particles[1].y) - abs(particles[0].y - particles[1].y)/2 - rotated_text.get_height()/2 + offsetY - world_offset[1])
        )
        
        pygame.draw.line(screen, colors.YELLOW, (particles[0].x - world_offset[0], particles[0].y-world_offset[1]), (particles[1].x - world_offset[0], particles[1].y - world_offset[1]), 4)
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
        # if real_pos[0]+p.radius >= 0 and real_pos[0]-p.radius <= screen_width and real_pos[1]+p.radius >= 0 and real_pos[1]-p.radius <= screen_height:
        p.render(screen, world_offset)

    
    pygame.display.flip()