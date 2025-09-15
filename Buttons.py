import pygame
import random
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))  # script folder
    return os.path.join(base_path, relative_path)

class HackerButton:
    def __init__(self, x, y, width, height, text, color=(0, 255, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.glow_color = (min(color[0]+100, 255), min(color[1]+100, 255), min(color[2]+100, 255))
        self.active = False
        self.glitch_offset = 0
        self.glitch_timer = 0
        
        try:
            self.font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 24)
        except:
            self.font = pygame.font.SysFont("Courier New", 24, bold=True)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.active = self.rect.collidepoint(mouse_pos)
        
        # Glitch effect when active
        if self.active:
            self.glitch_timer += 1
            if self.glitch_timer % 5 == 0:
                self.glitch_offset = random.randint(-2, 2)
        else:
            self.glitch_offset = 0
            
        # Draw command line style button
        color = self.glow_color if self.active else self.base_color
        pygame.draw.rect(surface, (0, 10, 0), self.rect)  # Dark background
        
        # Draw text with cursor and glitch effect
        text = f"> {self.text}{'_' if self.active else ''}"
        text_surf = self.font.render(text, True, color)
        surface.blit(text_surf, (self.rect.x + 10 + self.glitch_offset, 
                                self.rect.centery - text_surf.get_height()//2 + self.glitch_offset))
        
        # Draw subtle glow when active
        if self.active:
            glow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*color, 30), glow.get_rect(), 1)
            surface.blit(glow, self.rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False