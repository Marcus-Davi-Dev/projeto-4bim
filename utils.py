import math
import pygame
import constants.colors as colors

pygame.init()

def to_rad(deg: float) -> float:
    return deg/180*math.pi

def to_deg(rad: float) -> float:
    return rad*180/math.pi

def distance(pos1: tuple[float, float], pos2: tuple[float, float]):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def draw_grid(surface: pygame.Surface, squares_size: int, color: tuple[int, int, int] | tuple[int, int, int, int], offset: tuple[int, int] | tuple[float, float] | list[int] | list[float] = (0, 0)):
    """Draws the grid in which the particles will be. It does NOT render it, you have to use pygame.display.flip() or .update() manually."""
    for i in range(int(surface.get_width()/squares_size) + 1): # colunas
        pygame.draw.line(surface, color, (i*squares_size - offset[0]%squares_size, 0), (i*squares_size - offset[0]%squares_size, surface.get_height()))

    for i in range(int(surface.get_height()/squares_size) + 1): # linhas
        pygame.draw.line(surface, color, (0, i*squares_size - offset[1]%squares_size), (surface.get_width(), i*squares_size - offset[1]%squares_size))
        
def draw_ele_force_formula(surface: pygame.surface.Surface, pos: tuple[float, float], font: pygame.font.Font):
    size = font.get_height()
    Fe = font.render("Fe = k.", False, colors.BLACK)
    Q1Q2 = font.render("|Q1|.|Q2|", False, colors.BLACK)
    d2 = font.render("d²", False, colors.BLACK)
#2 texts in top of each other
#                           Two paddings of 0.05 for the line
#                                      line of size/8 size
    total_y_size = size*2 + 0.1*size + size/8
    division_size = font.size("|Q1|.|Q2|")[0]
    
    surface.blit(Fe, (pos[0], pos[1] + total_y_size/2 - size/2))
    x_offset = font.size("Fe = k.")[0]
    surface.blit(Q1Q2, (pos[0] + x_offset, pos[1]))
    surface.blit(d2, (pos[0] + x_offset + division_size/2 - font.size("d2")[0]/2, pos[1] + total_y_size - size))
    
    pygame.draw.line(surface, colors.BLACK, (pos[0] + x_offset, pos[1] + total_y_size/2), (pos[0] + x_offset + division_size, pos[1] + total_y_size/2), int(size/12))