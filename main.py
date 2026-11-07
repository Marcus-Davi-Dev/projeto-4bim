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
    "particle": None,
    "show_field": False,
}
action_side_menu_state: str = "wander"
side_menu_states = ["wander", "create particle", "inspect"]
side_menu_translations = {
    "wander": "mover pela grid",
    "create particle": "criar partículas",
    "inspect": "inspecionar"
}
side_menu_padding_x = 6
side_menu_padding_y = 10
side_menu_margin_x = 20
action_badge_size = 60
actions_gap = 10

side_menu_height = len(side_menu_states) * action_badge_size + (len(side_menu_states)-1) * actions_gap + side_menu_padding_y*2

try:
    move_cursor_img = pygame.transform.smoothscale(pygame.image.load("./imgs/move.jpg").convert_alpha(), (action_badge_size, action_badge_size))
except:
    move_cursor_img = pygame.Surface((action_badge_size, action_badge_size), pygame.SRCALPHA)
    pygame.draw.rect(move_cursor_img, (45, 47, 60), move_cursor_img.get_rect(), border_radius=8)
side_menu_state_images = [move_cursor_img]

state: str = "main_screen"
selected_lesson: int | None = None

general_font = "./fonts/Exo_2/Exo2-Regular.ttf"
title_font_file = "./fonts/Audiowide-Regular.ttf"
# the list of particles
particles: list[Particle] = []


# flags to track whether the user has clicked once or just kept the mouse firing inputs
mousePressedButtons = [False, False, False]

tooltip_font = pygame.font.Font(general_font, 14)

lessons = [
    {
        "title": "Carga elétrica",
        "summary": "Sinais, unidade e conservação da carga.",
        "paragraphs": [
            "A carga elétrica é uma propriedade da matéria. Existem cargas positivas e negativas; cargas de mesmo sinal se repelem e cargas de sinais opostos se atraem.",
            "No Sistema Internacional, a carga é medida em coulombs (C). A carga elementar tem módulo e = 1,602 x 10^-19 C. Prótons têm carga +e e elétrons, -e.",
            "Em um sistema isolado, a carga elétrica total se conserva: ela pode ser transferida entre corpos, mas não é criada nem destruída em processos comuns.",
        ],
    },
    {
        "title": "Força eletrostática",
        "summary": "Lei de Coulomb, direção e sentido da força.",
        "paragraphs": [
            "Duas cargas puntiformes q1 e q2, separadas por uma distância r no vácuo, exercem forças de mesma intensidade uma sobre a outra.",
            "F = k |q1 q2| / r², onde k ≈ 8,99 x 10^9 N·m²/C² no vácuo. A força atua ao longo da reta que liga as cargas.",
            "Cargas de mesmo sinal se repelem; cargas de sinais opostos se atraem. A força diminui com o quadrado da distância: ao dobrar r, sua intensidade cai para um quarto.",
        ],
    },
    {
        "title": "Campo elétrico",
        "summary": "Campo como força por unidade de carga de teste.",
        "paragraphs": [
            "O campo elétrico descreve a influência elétrica em cada ponto do espaço. Para uma carga de teste q, E = F/q; no SI, sua unidade é N/C (equivalente a V/m).",
            "Para uma carga puntiforme Q, o módulo do campo é E = k |Q| / r². O campo aponta para fora de uma carga positiva e para uma carga negativa.",
            "O campo resultante de várias cargas é a soma vetorial dos campos produzidos por cada uma. A carga de teste usada para definir o campo é considerada positiva.",
        ],
    },
    {
        "title": "Potencial e energia elétrica",
        "summary": "Energia potencial e diferença de potencial.",
        "paragraphs": [
            "O potencial elétrico V é a energia potencial elétrica por unidade de carga: V = U/q. Sua unidade é o volt (V), equivalente a joule por coulomb.",
            "Para uma carga puntiforme Q, tomando o potencial como zero no infinito, V = k Q/r. O potencial é uma grandeza escalar; contribuições de várias cargas são somadas algebricamente.",
            "A energia potencial de duas cargas puntiformes é U = (k*q1*q2)/r. Ela é positiva para cargas de mesmo sinal e negativa para cargas de sinais opostos.",
        ],
    },
    {
        "title": "Trabalho para mover uma carga",
        "summary": "Movimento entre A e B e conservação de energia.",
        "paragraphs": [
            "Ao mover uma carga q de A para B, a variação da energia potencial elétrica é ΔU = q (VB - VA) = q ΔV.",
            "O trabalho realizado pelo campo elétrico é Wcampo = -ΔU = q (VA - VB). Se o campo realiza trabalho positivo, a energia potencial diminui.",
            "Se a carga é deslocada lentamente sem variar sua energia cinética, o trabalho de um agente externo é Wexterno = ΔU. Em eletrostática, esse trabalho depende dos pontos inicial e final, não do caminho.",
        ],
    },
]

def particle_side_menu_layout():
    panel_width = min(340, screen_width)
    panel_x = screen_width - panel_width
    content_x = panel_x + 16
    content_width = panel_width - 32
    particle_section = pygame.Rect(content_x, 64, content_width, 278)
    global_section = pygame.Rect(content_x, 358, content_width, 112)
    return {
        "panel": pygame.Rect(panel_x, 0, panel_width, screen_height),
        "close": pygame.Rect(panel_x + panel_width - 42, 16, 24, 24),
        "particle": particle_section,
        "global": global_section,
        "field_toggle": pygame.Rect(content_x + 12, global_section.y + 52, 20, 20),
        "field_control": pygame.Rect(
            content_x + 8,
            global_section.y + 44,
            content_width - 16,
            42,
        ),
    }

def draw_electric_field_grid(surface, grid_spacing=40, k=8987551792):
    global particles, world_offset
    """
    Desenha o campo elétrico resultante como uma grade de setas na tela.
    """
    if len(particles) == 0:
        return

    screen_w, screen_h = surface.get_size()

    for screen_x in range(grid_spacing // 2, screen_w, grid_spacing):
        for screen_y in range(grid_spacing // 2, screen_h, grid_spacing):
            
            world_x = screen_x + world_offset[0]
            world_y = screen_y + world_offset[1]

            ex_total = 0.0
            ey_total = 0.0
            too_close = False

            for p in particles:
                dx = world_x - p.x
                dy = world_y - p.y
                r_sq = dx**2 + dy**2
                r = math.sqrt(r_sq)

                if r < p.radius:
                    too_close = True
                    break

                e_magnitude = (k * p.chargeMantissa) / r_sq
                
                ex_total += e_magnitude * (dx / r)
                ey_total += e_magnitude * (dy / r)

            if too_close:
                continue

            e_norm = math.hypot(ex_total, ey_total)
            if e_norm == 0:
                continue

            dir_x = ex_total / e_norm
            dir_y = ey_total / e_norm

            arrow_length = 16

            start_pt = (screen_x, screen_y)
            end_pt = (screen_x + dir_x * arrow_length, screen_y + dir_y * arrow_length)

            color = (0, 212, 255)

            pygame.draw.line(surface, color, start_pt, end_pt, 2)
            
            pygame.draw.circle(surface, color, (int(end_pt[0]), int(end_pt[1])), 2) # cabeça da seta

def show_actions_side_menu():
    side_menu_surf = pygame.Surface((action_badge_size + side_menu_padding_x * 2, side_menu_height), pygame.SRCALPHA)
    pygame.draw.rect(side_menu_surf, (30, 32, 45, 200), side_menu_surf.get_rect(), border_radius=12)
    screen.blit(side_menu_surf, (side_menu_margin_x, screen_height / 2 - side_menu_height / 2))
    
    offset_y = 0
    center = action_badge_size // 2
    color = (220, 220, 225)
    mouse_pos = pygame.mouse.get_pos()
    
    hovered_tooltip = None 
    
    for i, state in enumerate(side_menu_states):
        base_surf = side_menu_state_images[i].copy() if i < len(side_menu_state_images) else pygame.Surface((action_badge_size, action_badge_size), pygame.SRCALPHA)
        
        if i >= len(side_menu_state_images):
            pygame.draw.rect(base_surf, (45, 47, 60), base_surf.get_rect(), border_radius=8)
            
            if state == "create particle":
                pygame.draw.line(base_surf, color, (center, 15), (center, action_badge_size-15), 4)
                pygame.draw.line(base_surf, color, (15, center), (action_badge_size-15, center), 4)
            elif state == "inspect":
                pygame.draw.circle(base_surf, color, (center - 4, center - 4), 10, 3)
                pygame.draw.line(base_surf, color, (center + 3, center + 3), (center + 12, center + 12), 4)
        
        x_pos = side_menu_padding_x + side_menu_margin_x
        y_pos = screen_height / 2 - side_menu_height / 2 + side_menu_padding_y + offset_y
        
        button_rect = pygame.Rect(x_pos, y_pos, action_badge_size, action_badge_size)
        if button_rect.collidepoint(mouse_pos):
            hovered_tooltip = (state, y_pos)
        
        if state == action_side_menu_state:
            pygame.draw.rect(screen, globals["color"], (x_pos - 2, y_pos - 2, action_badge_size + 4, action_badge_size + 4), 3, border_radius=10)
            base_surf.set_alpha(255)
        else:
            base_surf.set_alpha(100) 
            
        screen.blit(base_surf, (x_pos, y_pos))
        offset_y += action_badge_size + actions_gap

    # tooltip
    if hovered_tooltip:
        state, btn_y = hovered_tooltip
        translation = side_menu_translations.get(state, state)
        
        text_surf = tooltip_font.render(translation, True, (240, 240, 245))
        
        # se Deus quiser eu acertei nos cálculos
        tt_x = side_menu_margin_x + side_menu_padding_x * 2 + action_badge_size + 15
        tt_y = btn_y + (action_badge_size / 2) - (text_surf.get_height() / 2)
        
        bg_rect = pygame.Rect(tt_x - 8, tt_y - 6, text_surf.get_width() + 16, text_surf.get_height() + 12)
        pygame.draw.rect(screen, (20, 22, 34), bg_rect, border_radius=6)
        pygame.draw.rect(screen, globals["color"], bg_rect, width=1, border_radius=6) # Bordinha com a cor de destaque
        
        screen.blit(text_surf, (tt_x, tt_y))

def show_particle_side_menu():
    if not side_menu["shown"] or side_menu["particle"] is None:
        return

    layout = particle_side_menu_layout()
    panel = layout["panel"]
    particle = side_menu["particle"]
    panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
    panel_surface.fill((20, 22, 34, 248))
    screen.blit(panel_surface, panel.topleft)
    pygame.draw.line(screen, (55, 60, 78), panel.topleft, (panel.left, screen_height), 1)

    heading_font = pygame.font.Font(general_font, 18)
    section_font = pygame.font.Font(general_font, 13)
    value_font = pygame.font.Font(general_font, 14)
    title = heading_font.render("INSPEÇÃO", True, (240, 240, 245))
    screen.blit(title, (panel.x + 16, 17))
    close_rect = layout["close"]
    pygame.draw.rect(screen, (45, 48, 62), close_rect, border_radius=6)
    close_text = value_font.render("x", True, (220, 220, 225))
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    particle_rect = layout["particle"]
    pygame.draw.rect(screen, (30, 33, 48), particle_rect, border_radius=10)
    pygame.draw.rect(screen, (55, 60, 78), particle_rect, width=1, border_radius=10)
    section_heading = section_font.render("PARTÍCULA", True, (130, 190, 230))
    screen.blit(section_heading, (particle_rect.x + 12, particle_rect.y + 12))

    if particle.chargeMantissa < 0:
        particle_name = "Elétron"
    elif particle.chargeMantissa > 0:
        particle_name = "Próton"
    else:
        particle_name = "Partícula neutra"
    particle_title = heading_font.render(particle_name, True, (240, 240, 245))
    screen.blit(particle_title, (particle_rect.x + 12, particle_rect.y + 34))

    details = [
        ("Carga", f"{particle.chargeMantissa:g} x 10^{particle.chargeExponent} C"),
        ("Posição", f"x: {particle.x:.1f}, y: {particle.y:.1f}"),
        ("Raio", f"{particle.radius:g} px"),
    ]
    detail_y = particle_rect.y + 72
    for label, value in details:
        label_surface = value_font.render(label, True, (155, 160, 175))
        value_surface = value_font.render(value, True, (225, 228, 235))
        screen.blit(label_surface, (particle_rect.x + 12, detail_y))
        screen.blit(value_surface, (particle_rect.x + 86, detail_y))
        detail_y += 26

    pygame.draw.line(
        screen,
        (55, 60, 78),
        (particle_rect.x + 12, detail_y + 2),
        (particle_rect.right - 12, detail_y + 2),
        1,
    )
    nearest_particle = min(
        (other for other in particles if other is not particle),
        key=lambda other: distance((particle.x, particle.y), (other.x, other.y)),
        default=None,
    )
    interaction_y = detail_y + 12
    interaction_label = value_font.render("Interação mais próxima", True, (155, 160, 175))
    screen.blit(interaction_label, (particle_rect.x + 12, interaction_y))
    if nearest_particle is None:
        interaction_text = "Nenhuma outra partícula"
    else:
        separation = distance(
            (particle.x, particle.y),
            (nearest_particle.x, nearest_particle.y),
        )
        if separation == 0:
            interaction_type = "Partículas sobrepostas"
        elif particle.chargeMantissa == 0 or nearest_particle.chargeMantissa == 0:
            interaction_type = "Sem interação elétrica"
        elif particle.chargeMantissa * nearest_particle.chargeMantissa < 0:
            interaction_type = "Atração"
        else:
            interaction_type = "Repulsão"
        interaction_text = f"{interaction_type} - d: {separation:.1f} px"
        if separation > 0:
            force_text = f"Força: {abs(particle.eletrostatic_force(nearest_particle)):.3g} N"
            force_surface = value_font.render(force_text, True, (225, 228, 235))
            screen.blit(force_surface, (particle_rect.x + 12, interaction_y + 42))
    interaction_surface = value_font.render(interaction_text, True, (225, 228, 235))
    screen.blit(interaction_surface, (particle_rect.x + 12, interaction_y + 20))

    global_rect = layout["global"]
    pygame.draw.rect(screen, (30, 33, 48), global_rect, border_radius=10)
    pygame.draw.rect(screen, (55, 60, 78), global_rect, width=1, border_radius=10)
    global_heading = section_font.render("GLOBAL", True, (130, 190, 230))
    screen.blit(global_heading, (global_rect.x + 12, global_rect.y + 12))
    field_label = value_font.render("Campo elétrico", True, (225, 228, 235))
    screen.blit(field_label, (global_rect.x + 42, global_rect.y + 52))
    field_rect = layout["field_toggle"]
    pygame.draw.rect(screen, (100, 105, 120), field_rect, 2, border_radius=4)
    if side_menu.get("show_field"):
        pygame.draw.rect(screen, globals["color"], field_rect.inflate(-6, -6), border_radius=2)
    field_hint = section_font.render("Mostrar o campo elétrico", True, (155, 160, 175))
    screen.blit(field_hint, (global_rect.x + 42, global_rect.y + 75))

def onclick(ev: pygame.event.Event):
    global state, action_side_menu_state, side_menu, selected_lesson
    if state == "main_screen":
        start_rect, lessons_rect = main_menu_layout()
        if start_rect.collidepoint(ev.pos):
            state = "sandbox"
        elif lessons_rect.collidepoint(ev.pos):
            selected_lesson = None
            state = "lessons"
        return

    if state == "lessons":
        back_rect = lessons_back_layout()
        if back_rect.collidepoint(ev.pos):
            if selected_lesson is None:
                state = "main_screen"
            else:
                selected_lesson = None
            return

        if selected_lesson is None:
            for index in range(len(lessons)):
                if lesson_card_layout(index).collidepoint(ev.pos):
                    selected_lesson = index
                    return
        return
    
    if state != "sandbox":
        return
    if side_menu_margin_x < ev.pos[0] < side_menu_margin_x + side_menu_padding_x*2+action_badge_size and (screen_height/2 - side_menu_height/2) < ev.pos[1] < (screen_height/2 + side_menu_height/2): # clicou no side menu das actions
        for i in range(len(side_menu_states)):
            if side_menu_margin_x + side_menu_padding_x < ev.pos[0] < side_menu_margin_x + side_menu_padding_x*2 + action_badge_size and (screen_height/2 - side_menu_height/2 + side_menu_padding_y + action_badge_size*i + actions_gap*max(i-1, 0)) < ev.pos[1] < (screen_height/2 - side_menu_height/2 + side_menu_padding_y + action_badge_size*(i+1) + actions_gap*max(i-1, 0)):
                action_side_menu_state = side_menu_states[i]
        return
    # state = "sandbox"
    
    if side_menu["shown"]:
        layout = particle_side_menu_layout()
        if layout["panel"].collidepoint(ev.pos):
            if layout["close"].collidepoint(ev.pos):
                side_menu["shown"] = False
                side_menu["particle"] = None
            elif layout["field_control"].collidepoint(ev.pos):
                side_menu["show_field"] = not side_menu["show_field"]
            return

    if action_side_menu_state == "wander":
        return
    
    if action_side_menu_state == "inspect":
        for particle in particles:
            world_pos = (ev.pos[0] + world_offset[0], ev.pos[1] + world_offset[1])
            if distance(world_pos, (particle.x, particle.y)) < particle.radius:
                side_menu['shown'] = True
                side_menu['particle'] = particle
                show_particle_side_menu()
                return
        
    if action_side_menu_state != "create particle":
        return
    
    
    particle_position = (
        ev.pos[0] + world_offset[0],
        ev.pos[1] + world_offset[1],
    )
    new_particle_radius = Particle.calculate_radius(-6)
    if any(
        distance(particle_position, (particle.x, particle.y))
        < particle.radius + new_particle_radius
        for particle in particles
    ):
        return

    charge = -20 if ev.button == 1 else 20
    particles.append(Particle(*particle_position, charge, -6))


clock = pygame.time.Clock()

globals = {
    "start_button_x": 0.0,
    "start_button_y": 0.0,
    "size": 80,
    # "color": (138, 43, 226)
    "color": (0, 153, 255)
}

def main_menu_layout():
    button_width = min(300, screen_width - 40)
    button_height = 56
    center_x = screen_width // 2
    return (
        pygame.Rect(center_x - button_width // 2, int(screen_height * 0.53), button_width, button_height),
        pygame.Rect(center_x - button_width // 2, int(screen_height * 0.53) + 74, button_width, button_height),
    )

def lessons_back_layout():
    button_width = min(240, screen_width - 40)
    return pygame.Rect(
        screen_width // 2 - button_width // 2,
        screen_height - 68,
        button_width,
        48,
    )

def lesson_card_layout(index: int):
    card_top = 142 if screen_height >= 650 else 105
    gap = 10
    available_height = screen_height - card_top - 138
    card_height = max(52, min(82, (available_height - gap * (len(lessons) - 1)) // len(lessons)))
    card_width = min(820, screen_width - 40)
    return pygame.Rect(
        screen_width // 2 - card_width // 2,
        card_top + index * (card_height + gap),
        card_width,
        card_height,
    )

def draw_button(surface: pygame.Surface, rect: pygame.Rect, label: str, font_size=22):
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    fill_color = (37, 43, 62) if hovered else (28, 32, 47)
    border_color = (75, 181, 235) if hovered else globals["color"]
    pygame.draw.rect(surface, fill_color, rect, border_radius=12)
    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=12)
    font = pygame.font.Font(general_font, font_size)
    text = font.render(label, True, (240, 242, 248))
    surface.blit(text, text.get_rect(center=rect.center))

def draw_wrapped_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    rect: pygame.Rect,
    line_gap=7,
):
    y = rect.y
    for paragraph in text.splitlines():
        if not paragraph:
            y += font.get_linesize()
            continue
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if line and font.size(candidate)[0] > rect.width:
                surface.blit(font.render(line, True, color), (rect.x, y))
                y += font.get_linesize() + line_gap
                line = word
            else:
                line = candidate
        if line:
            surface.blit(font.render(line, True, color), (rect.x, y))
            y += font.get_linesize() + line_gap
    return y

def main_screen(delta: float):
    global state, screen
    screen.fill((20, 22, 34))
    draw_grid(screen, 30, (31, 34, 48))
    
    title_size = min(60, max(32, screen_width // 16))
    title_font = pygame.font.Font(title_font_file, title_size)
    title_text = "Physics Sandbox"
    title = title_font.render(title_text, False, pygame.colordict.THECOLORS["aliceblue"])
    screen.blit(title, title.get_rect(center=(screen_width // 2, int(screen_height * 0.28))))
    subtitle_font = pygame.font.Font(general_font, 18)
    subtitle = subtitle_font.render("Explore as cargas e o campo elétrico", True, (165, 174, 193))
    screen.blit(subtitle, subtitle.get_rect(center=(screen_width // 2, int(screen_height * 0.38))))
    start_rect, lessons_rect = main_menu_layout()
    draw_button(screen, start_rect, "Abrir sandbox")
    draw_button(screen, lessons_rect, "Aulas de eletrostática")

def lessons_screen():
    screen.fill((20, 22, 34))
    draw_grid(screen, 30, (31, 34, 48))
    title_font = pygame.font.Font(general_font, min(34, max(24, screen_width // 30)))
    subtitle_font = pygame.font.Font(general_font, 16)
    body_font = pygame.font.Font(general_font, 17)
    muted = (165, 174, 193)
    light = (232, 235, 243)

    if selected_lesson is None:
        title = title_font.render("Aulas de eletrostática", True, light)
        screen.blit(title, title.get_rect(center=(screen_width // 2, 66)))
        subtitle = subtitle_font.render("Escolha um tema para começar", True, muted)
        screen.blit(subtitle, subtitle.get_rect(center=(screen_width // 2, 105)))
        for index, lesson in enumerate(lessons):
            card = lesson_card_layout(index)
            hovered = card.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(
                screen,
                (36, 42, 59) if hovered else (27, 31, 45),
                card,
                border_radius=10,
            )
            pygame.draw.rect(
                screen,
                (75, 181, 235) if hovered else (55, 62, 80),
                card,
                width=1,
                border_radius=10,
            )
            number_font = pygame.font.Font(general_font, 16)
            number = number_font.render(f"{index + 1:02}", True, (90, 190, 235))
            screen.blit(number, (card.x + 16, card.y + 13))
            card_title = subtitle_font.render(lesson["title"], True, light)
            screen.blit(card_title, (card.x + 58, card.y + 10))
            summary = pygame.font.Font(general_font, 14).render(lesson["summary"], True, muted)
            screen.blit(summary, (card.x + 58, card.y + 38))
    else:
        lesson = lessons[selected_lesson]
        title = title_font.render(lesson["title"], True, light)
        screen.blit(title, title.get_rect(center=(screen_width // 2, 67)))
        card_width = min(860, screen_width - 40)
        content = pygame.Rect(
            screen_width // 2 - card_width // 2,
            112,
            card_width,
            max(100, screen_height - 202),
        )
        pygame.draw.rect(screen, (27, 31, 45), content, border_radius=14)
        pygame.draw.rect(screen, (55, 62, 80), content, width=1, border_radius=14)
        text_rect = content.inflate(-40, -36)
        y = text_rect.y
        for paragraph in lesson["paragraphs"]:
            y = draw_wrapped_text(
                screen,
                paragraph,
                body_font,
                light,
                pygame.Rect(text_rect.x, y, text_rect.width, text_rect.bottom - y),
                line_gap=5,
            )
            y += 14

    draw_button(screen, lessons_back_layout(), "Voltar", font_size=18)

def draw_particle_interactions(surface: pygame.Surface):
    for index, particle in enumerate(particles):
        start = (particle.x - world_offset[0], particle.y - world_offset[1])
        for other in particles[index + 1:]:
            if particle.chargeMantissa == 0 or other.chargeMantissa == 0:
                continue

            end = (other.x - world_offset[0], other.y - world_offset[1])
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            separation = math.hypot(dx, dy)
            if separation == 0:
                continue

            direction = (dx / separation, dy / separation)
            attraction = particle.chargeMantissa * other.chargeMantissa < 0
            color = (70, 195, 220) if attraction else (245, 155, 95)

            line_start_distance = particle.radius + 3
            line_end_distance = separation - other.radius - 3
            if line_start_distance >= line_end_distance:
                continue

            line_start = (
                start[0] + direction[0] * line_start_distance,
                start[1] + direction[1] * line_start_distance,
            )
            line_end = (
                start[0] + direction[0] * line_end_distance,
                start[1] + direction[1] * line_end_distance,
            )
            clipped_line = surface.get_rect().clipline(line_start, line_end)
            if not clipped_line:
                continue
            line_start, line_end = clipped_line
            line_dx = line_end[0] - line_start[0]
            line_dy = line_end[1] - line_start[1]
            line_length = math.hypot(line_dx, line_dy)
            if line_length == 0:
                continue
            line_direction = (line_dx / line_length, line_dy / line_length)
            dash_length = 9
            gap_length = 7
            distance_along_line = 0
            while distance_along_line < line_length:
                dash_end_distance = min(
                    distance_along_line + dash_length,
                    line_length,
                )
                dash_start = (
                    line_start[0] + line_direction[0] * distance_along_line,
                    line_start[1] + line_direction[1] * distance_along_line,
                )
                dash_end = (
                    line_start[0] + line_direction[0] * dash_end_distance,
                    line_start[1] + line_direction[1] * dash_end_distance,
                )
                pygame.draw.line(surface, (28, 32, 43), dash_start, dash_end, 4)
                pygame.draw.line(surface, color, dash_start, dash_end, 2)
                distance_along_line += dash_length + gap_length

            if attraction:
                arrows = (
                    (start, direction, particle.radius + 22),
                    (end, (-direction[0], -direction[1]), other.radius + 22),
                )
            else:
                arrows = (
                    (start, (-direction[0], -direction[1]), particle.radius + 14),
                    (end, direction, other.radius + 14),
                )

            for arrow_center, arrow_direction, arrow_distance in arrows:
                arrow_tip = (
                    arrow_center[0] + arrow_direction[0] * arrow_distance,
                    arrow_center[1] + arrow_direction[1] * arrow_distance,
                )
                arrow_length = 8
                arrow_half_width = 4
                perpendicular = (-arrow_direction[1], arrow_direction[0])
                arrow_base = (
                    arrow_tip[0] - arrow_direction[0] * arrow_length,
                    arrow_tip[1] - arrow_direction[1] * arrow_length,
                )
                pygame.draw.polygon(surface, color, [
                    arrow_tip,
                    (
                        arrow_base[0] + perpendicular[0] * arrow_half_width,
                        arrow_base[1] + perpendicular[1] * arrow_half_width,
                    ),
                    (
                        arrow_base[0] - perpendicular[0] * arrow_half_width,
                        arrow_base[1] - perpendicular[1] * arrow_half_width,
                    ),
                ])

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
    draw_particle_interactions(screen)
    
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

running = True
while running:
    screen.fill(pygame.colordict.THECOLORS["white"]) # reset the screen
    delta = clock.tick()
    fps_text = f"FPS: {1000/max(delta, 1)}"
    if delta > 1000:
        fps_text = f"FPM: {60000/max(delta, 1)}"
    fps_surf = tooltip_font.render(fps_text, False, (0, 0, 0))
    
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
                side_menu["shown"] = False
                side_menu["particle"] = None
            if event.key == pygame.K_r:
                selected_lesson = None
                state = "main_screen"
            if event.key == pygame.K_ESCAPE and state == "lessons":
                if selected_lesson is None:
                    state = "main_screen"
                else:
                    selected_lesson = None
    screen_width, screen_height = screen.get_size()
    if state == "main_screen":
        main_screen(delta)
    elif state == "lessons":
        lessons_screen()
    elif state == "sandbox":
        if side_menu["show_field"]:
            draw_electric_field_grid(screen, 30)
        sandbox(delta)
        if side_menu["shown"]:
            show_particle_side_menu()
        show_actions_side_menu()

    screen.blit(fps_surf, (2, 2))
        
        
    pygame.display.flip()