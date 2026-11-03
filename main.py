import pygame
import sys
# import math
from particle import Particle
# import custom_font
from utils import *

pygame.display.init()
pygame.font.init()

# screen
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

GRID_SIZE = 50
world_offset = [0.0, 0.0]

base_movement_speed = 2.5
side_menu = {
    "shown": False,
    "particle": None
}
action_side_menu_state: str = "wander"
side_menu_states = ["wander", "create particle"]
side_menu_padding_x = 6
side_menu_padding_y = 10
side_menu_margin_x = 20
action_badge_size = 60
actions_gap = 10

side_menu_height = len(side_menu_states) * action_badge_size + (len(side_menu_states)-1) * actions_gap + side_menu_padding_y*2

state: str = "main_screen"

general_font = "./fonts/Exo_2/Exo2-Regular.ttf"
title_font_file = "./fonts/Audiowide-Regular.ttf"
# the list of particles
particles: list[Particle] = []

# move_cursor_img = pygame.image.load("./imgs/move.jpeg")

# flags to track whether the user has clicked once or just kept the mouse firing inputs
mousePressedButtons = [False, False, False]

def show_actions_side_menu():
    side_menu_surf = pygame.surface.Surface((action_badge_size+side_menu_padding_x*2, side_menu_height), pygame.SRCALPHA)
    side_menu_surf.fill((255, 0, 0, 255))
    
    
    screen.blit(side_menu_surf, (side_menu_margin_x, screen_height/2 - side_menu_height/2))
    offset_y = 0
    for i in range(len(side_menu_states)):
        surf = pygame.Surface((action_badge_size, action_badge_size))
        if side_menu_states[i] == action_side_menu_state:
            surf.fill((0, 150, 150, 0))
            screen.blit(surf, (side_menu_padding_x + side_menu_margin_x, screen_height/2 - side_menu_height/2 + side_menu_padding_y + offset_y))
        else:
            surf.fill((0, 0, 0, 0))
            screen.blit(surf, (side_menu_padding_x + side_menu_margin_x, screen_height/2 - side_menu_height/2 + side_menu_padding_y + offset_y))
            
        offset_y += action_badge_size + actions_gap

def show_particle_side_menu():
    global side_menu
    
    menu_offset = screen_width/5*4
    background = pygame.Surface((screen_width/5, screen_height), pygame.SRCALPHA)
    background.fill((50, 50, 50, 0))
    screen.blit(background, (screen_width/5*4, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    big_font = pygame.font.Font(general_font, 24)
    particle_text = "Elétron" if side_menu['particle'].chargeMantissa < 0 else "Próton"
    # charge_text = f"Carga da partícula: {side_menu['particle'].charge}"
    
    particle_surf = big_font.render(particle_text, False, pygame.colordict.THECOLORS["lightgray"])
    screen.blit(particle_surf, (menu_offset + 4, 4))

def onclick(ev: pygame.event.Event):
    global state, action_side_menu_state
    if state == "main_screen":
        if distance(ev.pos, (screen_width/2, screen_height/2)) < globals["size"]:
            state = "sandbox"
        return
    
    if state != "sandbox":
        return
    if side_menu_margin_x < ev.pos[0] < side_menu_margin_x + side_menu_padding_x*2+action_badge_size and (screen_height/2 - side_menu_height/2) < ev.pos[1] < (screen_height/2 + side_menu_height/2): # clicou no side menu das actions
        for i in range(len(side_menu_states)):
            if side_menu_margin_x + side_menu_padding_x < ev.pos[0] < side_menu_margin_x + side_menu_padding_x*2 + action_badge_size and (screen_height/2 - side_menu_height/2 + side_menu_padding_y + action_badge_size*i + actions_gap*max(i-1, 0)) < ev.pos[1] < (screen_height/2 - side_menu_height/2 + side_menu_padding_y + action_badge_size*(i+1) + actions_gap*max(i-1, 0)):
                action_side_menu_state = side_menu_states[i]
        return
    # state = "sandbox"
    
    if action_side_menu_state == "wander":
        return
    
    for particle in particles:
        if distance(ev.pos, (particle.x, particle.y)) < particle.radius:
            side_menu['shown'] = True
            side_menu['particle'] = particle
            show_particle_side_menu()
            return
        
    if action_side_menu_state != "create particle":
        return
    
    if len(particles) >= 2:
        return
    
    if len(particles) == 1 and distance(ev.pos, (particles[0].x, particles[0].y)) < particles[0].radius+Particle.calculate_radius(-6):
        return

    charge = -20 if ev.button == 1 else 20
    particles.append(Particle(ev.pos[0]+world_offset[0], ev.pos[1]+world_offset[1], charge, -6))


clock = pygame.time.Clock()

globals = {
    "start_button_x": 0.0,
    "start_button_y": 0.0,
    "size": 80,
    # "color": (138, 43, 226)
    "color": (0, 153, 255)
}

def main_screen(delta: float):
    global state, screen
    screen.fill((20, 22, 34))
    draw_grid(screen, 30, (35, 37, 50))
    
    title_size = 60
    title_font = pygame.font.Font(title_font_file, title_size)
    title_text = "Physics SandBox"
    title = title_font.render(title_text, False, pygame.colordict.THECOLORS["aliceblue"])
    screen.blit(title, (screen_width/2 - title_font.size(title_text)[0]/2, title_size))
        
    pygame.draw.circle(screen, globals['color'], (screen_width/2, screen_height/2), globals["size"])

    play_text_size = 32
    play_text_font = pygame.font.Font(general_font, play_text_size)
    play_text = "START"
    play_render = play_text_font.render(play_text, False, pygame.colordict.THECOLORS["white"])
    screen.blit(play_render, (screen_width/2 - play_text_font.size(play_text)[0]/2, screen_height/2 - play_text_size/2))
    
    if mousePressedButtons.count(True) > 0:
        pos = pygame.mouse.get_pos()
        if distance(pos, (screen_width/2, screen_height/2)) < globals["size"]:
            state = "sandbox"
            return
        
def sandbox(delta: float):
    global screen
    
    offset_increase = base_movement_speed * delta / 7
    pressed_keys = pygame.key.get_pressed()
    
    if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
        offset_increase *= 2
            
    if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
        world_offset[0] -= offset_increase
    if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
        world_offset[0] += offset_increase
    if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
        world_offset[1] -= offset_increase
    if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
        world_offset[1] += offset_increase
    
    draw_grid(screen, GRID_SIZE, pygame.colordict.THECOLORS["gray"], world_offset)
    
    info_font = pygame.font.Font(general_font, 14)
    
    if len(particles) == 2:
        potential_energy = info_font.render(f"Ptl energy: {particles[0].potential_energy(particles[1])}", False, pygame.colordict.THECOLORS["red"])
        screen.blit(potential_energy, (5, 5))
        
        potential = info_font.render(f"Ptl: {particles[0].potential(particles[1])}", False, pygame.colordict.THECOLORS["red"])
        screen.blit(potential, (5, 19))
        
        force = info_font.render(f"Eletrostatic force: {particles[0].eletrostatic_force(particles[1])}", False, pygame.colordict.THECOLORS["red"])
        screen.blit(force, (5, 34))
        
        field = info_font.render(f"Eletric field: {particles[0].eletric_field(particles[1])}", False, pygame.colordict.THECOLORS["red"])
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
        angle_font = pygame.font.Font(general_font, font_size)
        text = angle_font.render(f"{angle}", False, pygame.colordict.THECOLORS["green"])
        rotated_text = pygame.transform.rotate(text, angle)
        
        screen.blit(rotated_text, (
            max(particles[0].x, particles[1].x) - abs(particles[0].x - particles[1].x)/2 - rotated_text.get_width()/2 + offsetX - world_offset[0],
            max(particles[0].y, particles[1].y) - abs(particles[0].y - particles[1].y)/2 - rotated_text.get_height()/2 + offsetY - world_offset[1])
        )
        
        pygame.draw.line(screen, pygame.colordict.THECOLORS["yellow"], (particles[0].x - world_offset[0], particles[0].y-world_offset[1]), (particles[1].x - world_offset[0], particles[1].y - world_offset[1]), 4)
        
        # formula_font = pygame.font.Font(general_font, 32)
        # draw_ele_force_formula(screen, (
        #     max(particles[0].x, particles[1].x) - abs(particles[0].x - particles[1].x)/2,
        #     max(particles[0].y, particles[1].y) - abs(particles[0].y - particles[1].y)/2
        # ), formula_font)
        
    else:
        potential_energy = info_font.render(f"Ptl energy: 0", False, pygame.colordict.THECOLORS["red"])
        screen.blit(potential_energy, (5, 5))
        
        potential = info_font.render(f"Ptl: 0", False, pygame.colordict.THECOLORS["red"])
        screen.blit(potential, (5, 19))
        
        force = info_font.render(f"Eletrostatic force: 0", False, pygame.colordict.THECOLORS["red"])
        screen.blit(force, (5, 34))
        
        field = info_font.render(f"Eletric field: 0", False, pygame.colordict.THECOLORS["red"])
        screen.blit(field, (5, 48))
    
    helper_size = 18
    helper_font = pygame.font.Font(general_font, helper_size)
    help_text = helper_font.render("Use as setas direcionais ou WASD para mover a câmera.", False, pygame.colordict.THECOLORS["black"])
    screen.blit(help_text, (5, screen_height-helper_size))
    
    for p in particles:
        # if real_pos[0]+p.radius >= 0 and real_pos[0]-p.radius <= screen_width and real_pos[1]+p.radius >= 0 and real_pos[1]-p.radius <= screen_height:
        p.render(screen, world_offset)
        
    world_pos_size = 21
    world_pos_font = pygame.font.Font(general_font, world_pos_size)
    x_text = world_pos_font.render(f"X: {(lambda a, n: a[0] + "." + a[1].ljust(n, "0")[:n])(str(world_offset[0]).split("."), 4)}", False, pygame.colordict.THECOLORS["green"])
    y_text = world_pos_font.render(f"Y: {(lambda a, n: a[0] + "." + a[1].ljust(n, "0")[:n])(str(world_offset[1]).split("."), 4)}", False, pygame.colordict.THECOLORS["green"])
    screen.blits([
        (x_text, (screen_width - x_text.get_width(), screen_height - world_pos_size*2)),
        (y_text, (screen_width - y_text.get_width(), screen_height - world_pos_size))
    ])
    
    if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
        shift_is_pressed_text = helper_font.render("SHIFT PRESSIONADO", False, pygame.colordict.THECOLORS["blue"])
        screen.blit(shift_is_pressed_text, (screen_width - shift_is_pressed_text.get_width(), screen_height - world_pos_size*3))
    
    if side_menu["shown"]:
        show_particle_side_menu()
        

running = True
while running:
    screen.fill(pygame.colordict.THECOLORS["white"]) # reset the screen
    delta = clock.tick()
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
        if event.type == pygame.MOUSEMOTION and mousePressedButtons.count(True) > 0:
            world_offset[0] -= event.rel[0]
            world_offset[1] -= event.rel[1]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                particles = []
            if event.key == pygame.K_r:
                state = "main_screen"
    screen_width, screen_height = screen.get_size()
    if state == "main_screen":
        main_screen(delta)
    elif state == "sandbox":
        sandbox(delta)
        show_actions_side_menu()
        
    pygame.display.flip()