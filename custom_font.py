import pygame
import json
# import sys

class CustomFont:
    cached_surfaces: dict[str, pygame.Surface] = {}
    font_res: tuple[int, int] = (16, 16)
    ratio: float = font_res[1]/font_res[0]
    
    def render(self, text: str, size: int, color: tuple[int, int, int]) -> pygame.Surface:
        if len(self.cached_surfaces.keys()) == 0:
            raise NotImplementedError(f"The font hasn't been initiated yet. Please use custom_font.init() or {type(self)}.update_bitmap()")
        offset = 0
        surface = pygame.Surface((len(text)*size + (len(text)-1)*2*size,self.ratio*size))
        surface.fill((255, 255, 255))
        
        for char in text:
            char_surface: pygame.Surface | None = None
            if self.cached_surfaces.get(char, None) == None:
                char_surface = self.cached_surfaces["NO_CHAR"]
            else:
                char_surface = self.cached_surfaces[char]
            scaled_surface = pygame.transform.scale(char_surface, (self.ratio*size, size))
            surface.blit(scaled_surface, (offset, 0))
            offset += (self.ratio * size)
        # sys.exit()
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
        
        
def init():
    bitmap: dict[str, list[str]]
    with open("bitmap.json") as file:
        text = file.read()
        bitmap = json.loads(text)
    
        for char in bitmap.keys():
            surface = pygame.Surface((CustomFont.font_res[0], CustomFont.font_res[1]), pygame.SRCALPHA)
            # surface.
            for x in range(CustomFont.font_res[0]):
                for y in range(CustomFont.font_res[1]):
                    if bitmap[char][y][x] == "1":
                        surface.set_at((x, y), (0, 0, 0))
            CustomFont.cached_surfaces[char] = surface