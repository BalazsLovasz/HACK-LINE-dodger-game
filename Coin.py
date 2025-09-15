import pygame
import random
import math

class Coin:
    def __init__(self, x, y, current_time):
        self.x = x
        self.y = y
        self.size = 35  # Slightly increased size
        self.collected = False
        # Changed 100 to 75 to simplify, and adjusted weights accordingly
        self.value = random.choices([20, 50, 100], weights=[70, 25, 5])[0]
        self.spawn_time = current_time
        self.pulse_phase = 0
        
        # Initialize default font (will be set later)
        self.font = None  
        
        # Type-specific properties
        if self.value == 20:  # Common
            self.type = "DATA"
            self.color = (0, 255, 0)
            self.symbol = "0101"
            self.pulse_speed = 0.05
        elif self.value == 50:  # Uncommon
            self.type = "CRYPTO"
            self.color = (0, 255, 255)
            self.symbol = "Ξ"
            self.pulse_speed = 0.08
        else:  # Rare (now 75)
            self.type = "BITCOIN" # Changed type
            self.color = (255, 215, 0)
            self.symbol = "$" # Changed symbol - still using $ as it's common for "credits"
            self.pulse_speed = 0.12
            # Removed _create_spawn_effect call as it's no longer needed for simplification
        
        self.frames = self._create_frames()
        self.current_frame = 0
        self.current_size = self.size

    @classmethod
    def set_font(cls, font):
        cls._class_font = font

    def _create_frames(self):
        """Create frames without font dependency"""
        frames = []
        for i in range(6):
            frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            if self.value == 20:  # DATA coin
                # Binary pattern with grid lines for a circuit board feel
                grid_spacing = 8
                line_color_alpha = (*self.color, 50) # Semi-transparent lines
                
                # Draw horizontal grid lines
                for y_line in range(0, self.size, grid_spacing):
                    pygame.draw.line(frame, line_color_alpha, (0, y_line), (self.size, y_line), 1)
                # Draw vertical grid lines
                for x_line in range(0, self.size, grid_spacing):
                    pygame.draw.line(frame, line_color_alpha, (x_line, 0), (x_line, self.size), 1)

                # Add random "data" dots/squares
                for _ in range(self.size // 4): 
                    x_data = random.randint(0, self.size - 4)
                    y_data = random.randint(0, self.size - 4)
                    if random.random() > 0.4: # Probability to draw a "bit"
                        pygame.draw.rect(frame, self.color, (x_data, y_data, 4, 4))
            
            elif self.value == 50:  # CRYPTO coin
                # Hexagonal design with inner lines for a network/blockchain feel
                points = [
                    (self.size//2, 4),
                    (self.size-6, self.size//3),
                    (self.size-6, 2*self.size//3),
                    (self.size//2, self.size-4),
                    (6, 2*self.size//3),
                    (6, self.size//3)
                ]
                pygame.draw.polygon(frame, self.color, points, 2) # Thinner border

                # Inner lines connecting opposite vertices (like a network)
                pygame.draw.line(frame, self.color, points[0], points[3], 1)
                pygame.draw.line(frame, self.color, points[1], points[4], 1)
                pygame.draw.line(frame, self.color, points[2], points[5], 1)

                # Small circle in the center, symbolizing a node or core
                pygame.draw.circle(frame, self.color, (self.size//2, self.size//2), self.size//8, 1)
                
            else:  # 75 value - CREDIT coin (hacker theme)
                center_x, center_y = self.size // 2, self.size // 2
                radius = self.size // 2 - 4
                
                # Outer circuit-like border
                pygame.draw.circle(frame, self.color, (center_x, center_y), radius, 2)
                
                # Inner digital pattern (cross with small rectangles)
                line_length = radius * 0.7
                pygame.draw.line(frame, self.color, (center_x - line_length//2, center_y), 
                                 (center_x + line_length//2, center_y), 2)
                pygame.draw.line(frame, self.color, (center_x, center_y - line_length//2), 
                                 (center_x, center_y + line_length//2), 2)
                                 
                # Small "nodes" or "data points" at the ends of the cross
                rect_size = 4
                pygame.draw.rect(frame, self.color, (center_x - line_length//2 - rect_size//2, center_y - rect_size//2, rect_size, rect_size))
                pygame.draw.rect(frame, self.color, (center_x + line_length//2 - rect_size//2, center_y - rect_size//2, rect_size, rect_size))
                pygame.draw.rect(frame, self.color, (center_x - rect_size//2, center_y - line_length//2 - rect_size//2, rect_size, rect_size))
                pygame.draw.rect(frame, self.color, (center_x - rect_size//2, center_y + line_length//2 - rect_size//2, rect_size, rect_size))
                
                # Add some random small lines/dots for "data flow" effect
                for _ in range(self.size // 6):
                    start_x = random.randint(center_x - radius + 2, center_x + radius - 2)
                    start_y = random.randint(center_y - radius + 2, center_y + radius - 2)
                    end_x = random.randint(start_x - 3, start_x + 3)
                    end_y = random.randint(start_y - 3, start_y + 3)
                    pygame.draw.line(frame, (*self.color, 100), (start_x, start_y), (end_x, end_y), 1)

            frames.append(frame)
        return frames

    # Removed _create_spawn_effect method entirely as it's no longer used

    def update(self, scroll_speed, current_time):
        self.x -= scroll_speed
        self.pulse_phase += self.pulse_speed
        
        # Removed particle update logic as _create_spawn_effect is gone

        # Value-specific behaviors
        if self.value == 50:
            self.current_size = int(self.size * (1 + 0.2 * math.sin(self.pulse_phase)))
        elif self.value == 25: # This value is not used, might be a leftover from previous code. Keeping for now to avoid errors.
            self.current_rotation = 5 * math.sin(self.pulse_phase)
        else: # Now applies to the 75-value coin
            # Removed random frame updates to simplify
            pass # No special animation for the 75-value coin, keeping it simple

    def draw(self, screen):
        if not self.collected:
            # Removed particle drawing logic as _create_spawn_effect is gone
            
            # Draw coin
            frame = self.frames[self.current_frame].copy()
            
            if self.value == 50:
                # Glow effect
                glow = pygame.Surface((self.current_size, self.current_size), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*self.color, 30), 
                                 (self.current_size//2, self.current_size//2),
                                 self.current_size//2)
                screen.blit(glow, (self.x - (self.current_size-self.size)//2,
                                 self.y - (self.current_size-self.size)//2))
            
            if self.value == 25: # This value is not used, might be a leftover. Keeping for now.
                frame = pygame.transform.rotate(frame, self.current_rotation)
                screen.blit(frame, (self.x - (frame.get_width()-self.size)//2,
                                  self.y - (frame.get_height()-self.size)//2))
            else:
                screen.blit(frame, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collect(self):
        self.collected = True
        return self.value
    
    def snap_to_lane(self, lane_positions):
        closest_lane = min(lane_positions, key=lambda lane_y: abs(lane_y - self.y))
        self.y = closest_lane

class KeyCollectible:
    SPAWN_DELAY = 2000  # Class variable for spawn timing
    SIZE = 70

    def __init__(self, x, y, current_time):
        self.x = x
        self.y = y
        self.size = 50
        self.collected = False
        self.type = "KEY"
        self.spawn_time = current_time
        self.pulse_phase = 0
        self.pulse_speed = 0.08
        self.frames = self._create_frames()
        self.current_frame = 0

    @classmethod
    def can_spawn(cls, x, y, obstacles):
        """Class method to check if spawn location is valid"""
        test_rect = pygame.Rect(x, y, cls.SIZE, cls.SIZE)
        for obstacle in obstacles:
            if hasattr(obstacle, 'get_rect') and test_rect.colliderect(obstacle.get_rect()):
                return False
        return True

    def _create_frames(self):
        frames = []
        for i in range(6):
            frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            # Brighter keycard base (light blue-gray)
            card_color = (100, 120, 150)  # Lighter color
            pygame.draw.rect(frame, card_color, (5, 5, self.size-10, self.size-10), border_radius=5)
            
            # High-contrast magnetic strip
            pygame.draw.rect(frame, (20, 20, 30), (10, 15, self.size-20, 8))
            
            # Glowing gold chip
            pygame.draw.rect(frame, (255, 200, 50), (15, 30, 12, 10))
            pygame.draw.rect(frame, (255, 240, 100), (15, 30, 12, 10), 1)
            
            # Pulsing blue glow (more visible)
            glow_intensity = 0.5 + 0.5 * math.sin(self.pulse_phase + i)
            glow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            glow_radius = int(self.size * (0.8 + 0.2 * math.sin(self.pulse_phase)))
            pygame.draw.circle(
                glow, 
                (0, 150, 255, int(100 * glow_intensity)),
                (self.size//2, self.size//2),
                glow_radius,
                3
            )
            frame.blit(glow, (0, 0))
            
            # Add blinking red LED
            if i % 2 == 0:  # Blink every other frame
                pygame.draw.circle(frame, (255, 40, 40), (self.size-10, 10), 3)
            
            frames.append(frame)
        return frames

    def update(self, scroll_speed):
        self.x -= scroll_speed
        self.pulse_phase += self.pulse_speed
        self.current_frame = int(self.pulse_phase * 3) % len(self.frames)

    def draw(self, screen):
        if not self.collected:
            screen.blit(self.frames[self.current_frame], (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collect(self):
        self.collected = True
        return 0

class GlitchCollectible:
    SPAWN_DELAY = 3000
    SIZE = 80
    PATTERN_RADIUS = 90
    PATTERN_COUNT = 6

    def __init__(self, x, y, current_time):
        self.x = x
        self.y = y
        self.size = 50
        self.collected = False
        self.type = "GLITCH"
        self.spawn_time = current_time
        self.pulse_phase = 0
        self.pulse_speed = 0.12
        self.frames = self._create_frames()
        self.current_frame = 0
        self.last_frame_update = 0

    @classmethod
    def can_spawn_pattern(cls, center_x, center_y, obstacles):
        """Check if the entire glitch pattern can spawn"""
        test_radius = cls.PATTERN_RADIUS + cls.SIZE
        test_rect = pygame.Rect(
            center_x - test_radius,
            center_y - test_radius,
            test_radius * 2,
            test_radius * 2
        )
        for obstacle in obstacles:
            if hasattr(obstacle, 'get_rect') and test_rect.colliderect(obstacle.get_rect()):
                return False
        return True
    
    def _create_frames(self):
        frames = []
        base_colors = [
            (180, 0, 255),  # Purple
            (255, 0, 180),  # Pink
            (0, 180, 255)   # Blue
        ]
        
        # Pre-create 4 frames instead of 8
        for i in range(4):
            frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            # Solid core with outline
            core_color = base_colors[i % len(base_colors)]
            pygame.draw.circle(frame, core_color, (self.size//2, self.size//2), self.size//2 - 4)
            pygame.draw.circle(frame, (255, 255, 255), (self.size//2, self.size//2), self.size//2 - 4, 2)
            
            # Add 3-5 glitch lines (reduced from 12)
            for _ in range(random.randint(3, 5)):
                start_x = random.randint(5, self.size-5)
                start_y = random.randint(5, self.size-5)
                end_x = start_x + random.randint(-10, 10)
                end_y = start_y + random.randint(-10, 10)
                pygame.draw.line(
                    frame, 
                    (random.randint(200, 255), 0, random.randint(200, 255)),
                    (start_x, start_y), (end_x, end_y), 
                    1
                )
            
            frames.append(frame)
        return frames

    def update(self, scroll_speed):
        self.x -= scroll_speed
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > 100:  # Update every 100ms
            self.pulse_phase += self.pulse_speed
            self.current_frame = int(self.pulse_phase) % len(self.frames)
            self.last_frame_update = now

    def draw(self, screen):
        if not self.collected:
            screen.blit(self.frames[self.current_frame], (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def collect(self):
        self.collected = True
        return 30
