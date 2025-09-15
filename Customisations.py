import pygame
import random

class Skin:
    def __init__(self, name, base_color, cost, pattern=None, border_radius=10):
        self.name = name
        self.base_color = base_color
        self.cost = cost
        self.pattern = pattern
        self.border_radius = border_radius

    def draw_preview(self, surface, rect):
        # Drop shadow
        shadow_offset = 6
        shadow_rect = rect.move(shadow_offset, shadow_offset)
        pygame.draw.rect(surface, (20, 40, 20), shadow_rect, border_radius=self.border_radius)

        # Neon border
        pygame.draw.rect(surface, (0, 255, 100), rect.inflate(10, 10), width=4, border_radius=self.border_radius+6)

        # Main rectangle
        pygame.draw.rect(surface, self.base_color, rect, border_radius=self.border_radius)

        # Pattern overlay
        if self.pattern:
            self.pattern(surface, rect)

        # Inner border for depth
        pygame.draw.rect(surface, (0, 0, 0), rect, width=2, border_radius=self.border_radius)

    def draw_robot(self, surface, rect, skin):
        # Create a temporary surface for the robot with per-pixel alpha
        temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        temp = temp.convert_alpha()

        # Draw base rectangle
        pygame.draw.rect(temp, self.base_color, temp.get_rect(), border_radius=1)

        # Draw pattern (clipped to robot shape)
        if self.pattern:
            self.pattern(temp, temp.get_rect())

        # Blit the robot to the main surface
        surface.blit(temp, rect.topleft)

        if(skin.name != "None"):
            # Draw neon border on main surface (so it glows outside the robot)
            pygame.draw.rect(surface, (0, 255, 100), rect.inflate(2, 2), width=2, border_radius=1)

class Trail:
    def __init__(self, name, effect_function, cost, color=(0,255,0)):
        self.name = name
        self.effect_function = effect_function
        self.cost = cost
        self.color = color

    def get_color(self):
        return self.color

    def draw_trail(self, surface, position):
        # The print statement was for debugging, can be removed in final code
        # print("Drawing trail at", position)
        self.effect_function(surface, position)

    def draw_preview(self, surface, rect):
        center = rect.center
        radius = min(rect.width, rect.height) // 4
        pygame.draw.circle(surface, (0, 255, 0), center, radius, 2)
        pygame.draw.circle(surface, (0, 255, 255), center, radius-4, 1)

# === Pattern Functions ===

def striped_pattern(surface, rect):
    # Neon green stripes, hacker style
    stripe_color = (0, 255, 100)
    stripe_width = 10
    for x in range(rect.left, rect.right, stripe_width * 2):
        stripe_rect = pygame.Rect(x, rect.top, stripe_width, rect.height)
        pygame.draw.rect(surface, stripe_color, stripe_rect, border_radius=4)

def icy_pattern(surface, rect):
    # Hacker blue ice with cracks and glow
    frost_color = (180, 255, 255)
    glow_color = (0, 255, 255)
    pygame.draw.rect(surface, glow_color, rect.inflate(8, 8), border_radius=rect.width//7)
    # Fractal-like cracks
    for _ in range(5):
        x1 = random.randint(rect.left+5, rect.right-5)
        y1 = random.randint(rect.top+5, rect.bottom-5)
        x2 = random.randint(rect.left+5, rect.right-5)
        y2 = random.randint(rect.top+5, rect.bottom-5)
        pygame.draw.line(surface, frost_color, (x1, y1), (x2, y2), 2)
    # Frost sparkles
    for _ in range(8):
        x = random.randint(rect.left+5, rect.right-5)
        y = random.randint(rect.top+5, rect.bottom-5)
        pygame.draw.circle(surface, (255, 255, 255), (x, y), 1)

def glow_pattern(surface, rect):
    # Pulsing blue glow
    glow_color = (0, 255, 255)
    for i in range(1, 4):
        pygame.draw.rect(surface, glow_color, rect.inflate(i*10, i*10), width=2, border_radius=rect.width//6+i*2)

def honeycomb_pattern(surface, rect):
    # Hacker-style hex grid
    dot_color = (255, 255, 0)
    spacing = 7
    r = 3
    for y in range(rect.top, rect.bottom, spacing):
        offset = (y // spacing) % 2 * (spacing // 2)
        for x in range(rect.left + offset, rect.right, spacing):
            pygame.draw.circle(surface, dot_color, (x, y), r, 1)
            pygame.draw.circle(surface, (0, 255, 0), (x, y), r-2, 1)

def matrix_pattern(surface, rect):
    # Matrix rain effect
    chars = "01"
    # Even smaller font and very few characters to ensure maximum spread
    font = pygame.font.SysFont("Consolas", 8, bold=True) # Changed from 7 to 6
    num_chars = 4 # Changed from 6 to 4 (very few characters for sparsity)

    for _ in range(num_chars):
        # Get approximate size of a rendered character to ensure it fits within bounds
        char_width, char_height = font.size("0")

        # Allow characters to spawn anywhere within the rect,
        # ensuring they don't go outside the boundaries.
        # The max() function handles cases where the rect might be smaller than the char.
        x = random.randint(rect.left, max(rect.left, rect.right - char_width - 1))
        y = random.randint(rect.top, max(rect.top, rect.bottom - char_height - 1))

        char = random.choice(chars)
        char_surf = font.render(char, True, (0, 255, 0))
        surface.blit(char_surf, (x, y))

def circuit_pattern(surface, rect):
    # Futuristic circuit lines
    neon = (0, 255, 100)
    for _ in range(6):
        x1 = random.randint(rect.left+10, rect.right-10)
        y1 = random.randint(rect.top+10, rect.bottom-10)
        x2 = x1 + random.choice([-1, 1]) * random.randint(20, 40)
        y2 = y1 + random.choice([-1, 1]) * random.randint(20, 40)
        pygame.draw.line(surface, neon, (x1, y1), (x2, y2), 2)
        pygame.draw.circle(surface, neon, (x2, y2), 3, 1)

# === Trail Effects ===

def fire_trail(surface, position):
    # Reduced particle size
    pygame.draw.circle(surface, (255, 120, 0), position, 5) # Reduced from 8 to 5
    pygame.draw.circle(surface, (255, 200, 100), position, 2) # Reduced from 4 to 2

def ice_trail(surface, position):
    # Reduced particle size
    pygame.draw.circle(surface, (100, 200, 255), position, 5) # Reduced from 8 to 5
    pygame.draw.circle(surface, (220, 240, 255), position, 2) # Reduced from 4 to 2

def matrix_trail(surface, position):
    # Reduced particle size
    pygame.draw.circle(surface, (0, 255, 0), position, 6, 2) # Reduced from 8 to 5
    pygame.draw.circle(surface, (0, 255, 100), position, 3, 1) # Reduced from 4 to 2

# === Skin & Trail Definitions ===

skins = [
    Skin("None", (255, 255, 255), 0, pattern=None, border_radius=10),  # White rectangle, always free
    Skin("Slime", (100, 200, 100), 3000, pattern=circuit_pattern, border_radius=10),
    Skin("Striped Green", (30, 180, 60), 3000, striped_pattern, border_radius=10),
    Skin("Ice", (120, 200, 255), 3000, icy_pattern, border_radius=10),
    Skin("Glow Blue", (80, 180, 255), 4000, glow_pattern, border_radius=10),
    Skin("Samuri", (40, 40, 40), 5000, honeycomb_pattern, border_radius=10),
    Skin("Matrix", (10, 30, 10), 5000, matrix_pattern, border_radius=10),
]

trails = [
    Trail("None", lambda s, p: None, 0, color=None),
    Trail("Fire", fire_trail, 4000, color=(255, 100, 0)),
    Trail("Ice", ice_trail, 4000, color=(100, 200, 255)),
    Trail("Matrix", matrix_trail, 5000, color=(0, 255, 0)),
]