import pygame
import json
import constants.colors as colors

def add_outline(surface: pygame.Surface, size: tuple[int, int]):
    for i in range(size[0]):
        for j in range(size[1]):
            if 180 > surface.get_at((i, j))[3] > 60:
                surface.set_at((i, j), (0, 0, 0, 255))

class CustomFont:
    cached_surfaces: dict[str, pygame.Surface] = {}
    font_res: tuple[int, int] = (16, 16)
    ratio: float = font_res[1]/font_res[0]
    
    def render(self, text: str, size: int, color: tuple[int, int, int] | tuple[int, int, int, int], scale="crisp") -> pygame.Surface:
        if len(self.cached_surfaces.keys()) == 0:
            raise NotImplementedError(f"The font hasn't been initiated yet. Please use custom_font.init() or {type(self)}.update_bitmap()")
        offset = 0
        surface = pygame.Surface((len(text)*self.ratio*size,size), pygame.SRCALPHA)
        
        for char in text:
            char_surface: pygame.Surface | None = None
            if self.cached_surfaces.get(char, None) == None:
                char_surface = self.cached_surfaces["NO_CHAR"]
            else:
                char_surface = self.cached_surfaces[char]

            surf = char_surface.copy()
            surf.fill(color)
            
            char_surface.set_colorkey(colors.BLACK)
            mask = pygame.mask.from_surface(char_surface)
            mask.invert()
            mask = mask.to_surface(unsetcolor=(0, 0, 0, 0))
            
            surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            scaled_surface = pygame.transform.smoothscale(surf, (self.ratio*size, size))
            add_outline(scaled_surface, scaled_surface.get_size())
            surface.blit(scaled_surface, (offset, 0))
            offset += (self.ratio * size)
        return surface
    
    def update_char(self, char, surface):
        self.cached_surfaces[char] = surface
    
    def update_bitmap(self, bitmap: dict[str, list[str]]):
        x_size = len(list(bitmap.values())[0][0])
        y_size = len(list(bitmap.values())[0])
        self.font_res = (x_size, y_size)
        self.ratio = y_size/x_size
        for char in bitmap.keys():
            surface = pygame.Surface((x_size, y_size), pygame.SRCALPHA)
            for x in range(x_size):
                for y in range(y_size):
                    if bitmap[char][y][x] == "1":
                        surface.set_at((x, y), (0, 0, 0))
            CustomFont.cached_surfaces[char] = surface
    
    def calculate_width(self, text: str, size: int):
        return len(text)*size*self.ratio
        
def init():
    bitmap: dict[str, list[str]]
    with open("bitmap.json") as file:
        text = file.read()
        bitmap = json.loads(text)
    
        for char in bitmap.keys():
            surface = pygame.Surface((CustomFont.font_res[0], CustomFont.font_res[1]), pygame.SRCALPHA)
            for x in range(CustomFont.font_res[0]):
                for y in range(CustomFont.font_res[1]):
                    if bitmap[char][y][x] == "1":
                        surface.set_at((x, y), (0, 0, 0))
            CustomFont.cached_surfaces[char] = surface