import pygame
import random
import math

class Obstacle:
    def __init__(self, screen_width, screen_height, obstacle_type=None):
        self.__width = 20
        self.__x = screen_width + 50  # Start off-screen right
        self.__color = (255, 50, 0)  # Base firewall color
        self.__particles = []

        

        if obstacle_type is None:
            obstacle_type = random.choice([0, 1, 2])  # 0: top, 1: bottom, 2: floating

        if obstacle_type == 0:
            self.__y = 0
            self.__height = random.randint(int(screen_height * 0.2), int(screen_height * 0.4))
            self.__type = "top"
        elif obstacle_type == 1:
            self.__height = random.randint(int(screen_height * 0.2), int(screen_height * 0.4))
            self.__y = screen_height - self.__height
            self.__type = "bottom"
        else:
            self.__height = random.randint(int(screen_height * 0.2), int(screen_height * 0.4))
            self.__y = random.randint(int(screen_height/2 - self.__height*0.8), int(screen_height/2 - self.__height*0.3))            
            self.__type = "floating"


    def update(self, scroll_speed):
        self.__x -= scroll_speed

        # Update particles
        for p in self.__particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.__particles.remove(p)

        # Generate flame particles
        if random.random() < 0.3:
            self.__particles.append({
                'x': self.__x + random.randint(0, self.__width),
                'y': self.__y + random.randint(0, self.__height),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'life': random.randint(10, 30),
                'size': random.randint(1, 3)
            })

    def draw(self, surface):
        # Fiery obstacle
        for i in range(self.__width):
            alpha = 200 - abs(i - self.__width // 2) * 10
            pygame.draw.rect(surface, (*self.__color, alpha),
                                (self.__x + i, self.__y, 1, self.__height))

        # Flame particles
        for p in self.__particles:
            alpha = min(255, p['life'] * 8)
            pygame.draw.circle(
                surface,
                (255, random.randint(100, 200), 0, alpha),
                (int(p['x']), int(p['y'])),
                p['size']
            )

        # Glitch effect
        if random.random() < 0.1:
            glitch_y = self.__y + random.randint(0, self.__height)
            pygame.draw.line(
                surface, (0, 255, 0, 100),
                (self.__x - 5, glitch_y),
                (self.__x + self.__width + 5, glitch_y),
                1
            )

    # Getters
    def get_x_coord(self): return self.__x
    def get_y_coord(self): return self.__y
    def get_height(self): return self.__height
    def get_width(self): return self.__width
    def get_rect(self): return pygame.Rect(self.__x, self.__y, self.__width, self.__height)
    def is_off_screen(self): return self.__x + self.__width < 0
    def get_type(self): return self.__type



class PairedObstacle:
    GAP_HEIGHT = 100  # vertical gap between top and bottom obstacles

    def __init__(self, screen_width, screen_height, lane_y_positions):
        self.__width = 20
        self.__x = screen_width + 50
        self.__color = (255, 50, 0)
        self.__particles_top = []
        self.__particles_bottom = []

        # Choose a lane for the gap
        gap_lane_index = random.randint(0, len(lane_y_positions) - 1)
        gap_y = lane_y_positions[gap_lane_index]

        # Top obstacle bottom edge just above gap_y
        self.__top_height = gap_y - self.GAP_HEIGHT // 2
        self.__top_y = 0

        # Bottom obstacle top edge just below gap_y
        self.__bottom_y = gap_y + self.GAP_HEIGHT // 2
        self.__bottom_height = screen_height - self.__bottom_y

    def update(self, scroll_speed):
        self.__x -= scroll_speed

        # Update particles top
        for p in self.__particles_top[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.__particles_top.remove(p)

        if random.random() < 0.3:
            self.__particles_top.append({
                'x': self.__x + random.randint(0, int(self.__width)),
                'y': int(self.__top_y) + random.randint(0, int(self.__top_height)),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'life': random.randint(10, 30),
                'size': random.randint(1, 3)
            })

        # Update particles bottom
        for p in self.__particles_bottom[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.__particles_bottom.remove(p)

        if random.random() < 0.3:
            self.__particles_bottom.append({
                'x': self.__x + random.randint(0, int(self.__width)),
                'y': int(self.__bottom_y) + random.randint(0, int(self.__bottom_height)),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'life': random.randint(10, 30),
                'size': random.randint(1, 3)
            })

    def draw(self, surface):
        
        # Draw top obstacle (vertical bar)
        for i in range(self.__width):
            alpha = 200 - abs(i - self.__width // 2) * 10
            pygame.draw.rect(surface, (*self.__color, alpha),
                            (self.__x + i, self.__top_y, 1, self.__top_height))

        # Draw bottom obstacle
        for i in range(self.__width):
            alpha = 200 - abs(i - self.__width // 2) * 10
            pygame.draw.rect(surface, (*self.__color, alpha),
                            (self.__x + i, self.__bottom_y, 1, self.__bottom_height))

        # Draw flame particles top
        for p in self.__particles_top:
            alpha = min(255, p['life'] * 8)
            pygame.draw.circle(
                surface,
                (255, random.randint(100, 200), 0, alpha),
                (int(p['x']), int(p['y'])),
                p['size']
            )

        # Draw flame particles bottom
        for p in self.__particles_bottom:
            alpha = min(255, p['life'] * 8)
            pygame.draw.circle(
                surface,
                (255, random.randint(100, 200), 0, alpha),
                (int(p['x']), int(p['y'])),
                p['size']
            )

        # Glitch effect top
        if random.random() < 0.1:
            glitch_y = int(self.__top_y) + random.randint(0, int(self.__top_height))
            pygame.draw.line(
                surface, (0, 255, 0, 100),
                (self.__x - 5, glitch_y),
                (self.__x + self.__width + 5, glitch_y),
                1
            )

        # Glitch effect bottom
        if random.random() < 0.1:
            glitch_y = int(self.__bottom_y) + random.randint(0, int(self.__bottom_height))
            pygame.draw.line(
                surface, (0, 255, 0, 100),
                (self.__x - 5, glitch_y),
                (self.__x + self.__width + 5, glitch_y),
                1
            )


    def get_x_coord(self): return self.__x
    def get_top_y(self): return self.__top_y
    def get_bottom_y(self): return self.__bottom_y
    def get_top_height(self): return self.__top_height
    def get_bottom_height(self): return self.__bottom_height
    def get_width(self): return self.__width
    def get_top_rect(self): return pygame.Rect(self.__x, self.__top_y, self.__width, self.__top_height)
    def get_bottom_rect(self): return pygame.Rect(self.__x, self.__bottom_y, self.__width, self.__bottom_height)
    def is_off_screen(self): return self.__x + self.__width < 0
    
class MovingObstacle:
    def __init__(self, screen_width, screen_height):
        self.__width = 20
        self.__height = random.randint(int(screen_height * 0.075), int(screen_height * 0.125))
        self.__x = screen_width + 50
        self.__oscillate_time = 0
        self.__speed = random.uniform(0.02, 0.045)
        self.__type = "oscillating"
        self.__color = (255, 50, 0)
        self.__particles = []

        # Lane setup
        lanes = [screen_height * 0.1, screen_height * 0.5, screen_height * 0.9]

        # Choose amplitude and determine base_y from center of lane(s)
        self.__amplitude = random.choice([150, 150, 270, 380])

        if self.__amplitude == 150:
            # Small amplitude → just oscillate around one lane
            self.__base_y = random.choice(lanes)
        elif self.__amplitude == 270:
            # Medium → between two lanes
            pairs = [(lanes[0], lanes[1]), (lanes[1], lanes[2])]
            low, high = random.choice(pairs)
            self.__base_y = ((low + high) // 2)
        else:
            # Large amplitude → center between top and bottom lanes
            self.__base_y = ((lanes[0] + lanes[2]) // 2)

        self.__y = self.__base_y - (self.__height/2)

    def update(self, scroll_speed):
        self.__x -= scroll_speed
        self.__oscillate_time += 1
        self.__y = self.__base_y + math.sin(self.__oscillate_time * self.__speed) * self.__amplitude

        # Update particles
        for p in self.__particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.__particles.remove(p)

        if random.random() < 0.3:
            self.__particles.append({
                'x': self.__x + random.randint(0, self.__width),
                'y': self.__y + random.randint(0, int(self.__height)),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'life': random.randint(10, 30),
                'size': random.randint(1, 3)
            })

    def draw(self, surface):
        
        for i in range(self.__width):
            alpha = 200 - abs(i - self.__width // 2) * 10
            pygame.draw.rect(surface, (*self.__color, alpha),
                            (self.__x + i, int(self.__y), 1, self.__height))

        for p in self.__particles:
            alpha = min(255, p['life'] * 8)
            pygame.draw.circle(
                surface,
                (255, random.randint(100, 200), 0, alpha),
                (int(p['x']), int(p['y'])),
                p['size']
            )

        if random.random() < 0.1:
            glitch_y = int(self.__y) + random.randint(0, int(self.__height))
            pygame.draw.line(
                surface, (0, 255, 0, 100),
                (self.__x - 5, glitch_y),
                (self.__x + self.__width + 5, glitch_y),
                1
            )


    def get_x_coord(self): return self.__x
    def get_y_coord(self): return self.__y
    def get_height(self): return self.__height
    def get_width(self): return self.__width
    def is_off_screen(self): return self.__x + self.__width < 0
    def get_type(self): return self.__type
    def get_rect(self): return pygame.Rect(self.__x, self.__y, self.__width, self.__height)
    def is_off_screen(self): return self.__x + self.__width < 0
