import pygame
import random
from Customisations import skins, trails

class Robot:
    def __init__(self, x, y, width, height):
        self.__x_coord = float(x)
        self.__y_coord = float(y)
        self.__width = width
        self.__height = height
        self.__color = (255, 255, 255)
        self.__speed = 12
        self.skin = next((s for s in skins if s.name == "None"), None)
        self.trail = next((s for s in trails if s.name == "None"), None)

        # Glitch effect variables
        self.glitch_active = False
        self.glitch_timer = 0
        self.glitch_duration = 150  # ms
        self.last_glitch_tick = 0

        # Dash variables
        self.original_x = x
        self.returning = False
        self.return_speed = 0
        self.dashing = False
        self.dash_distance = 150
        self.dash_speed = 20
        self.dash_target = 0
        self.dash_cooldown = 300  # ms
        self.last_dash_time = 0
        self.dash_direction = 0  # -1 for left, 1 for right, 0 no dash

        #trail variables
        self.trail_positions = []
        self._last_trail_pos = None
        self._just_interpolated = False

        # Particle variables
        self.active_particles = []
        self.max_particles = 10  # Reduced max particles
        self.particle_spawn_chance_normal = 0.05 # 5% chance during normal movement interpolation
        self.particle_spawn_chance_segment = 0.3 # 30% chance per step during segment interpolation (dashes/lane switches)


    def get_rect(self):
        return pygame.Rect(self.__x_coord, self.__y_coord, self.__width, self.__height)

    def draw(self, surface):
        now = pygame.time.get_ticks()

        # 1. Draw the main line trail with fading
        if self.trail and len(self.trail_positions) > 1 and self.trail.get_color() is not None:
            points = self.trail_positions
            n = len(points)
            base_color = self.trail.get_color()
            for i in range(n - 1):
                fade = (i + 1) / n
                color = (
                    int(base_color[0] * fade),
                    int(base_color[1] * fade),
                    int(base_color[2] * fade)
                )
                pygame.draw.line(surface, color, points[i], points[i + 1], 4)

        # 2. Draw particles using the trail's effect_function
        if self.trail and self.trail.name != "None":
            for particle_pos in self.active_particles:
                self.trail.draw_trail(surface, particle_pos)

        # 3. Draw robot skin
        rect = pygame.Rect(self.__x_coord, self.__y_coord, self.__width, self.__height)
        self.skin.draw_robot(surface, rect, self.skin)

        # 4. Draw glitch effect (existing logic)
        if self.glitch_active:
            delta = now - self.last_glitch_tick
            self.glitch_timer -= delta
            self.last_glitch_tick = now

            for _ in range(5):
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                glitch_rect = pygame.Rect(
                    self.__x_coord + offset_x,
                    self.__y_coord + offset_y,
                    self.__width,
                    self.__height,
                )
                glitch_color = random.choice([(0, 255, 255), (0, 255, 0), (255, 0, 255)])
                pygame.draw.rect(surface, glitch_color, glitch_rect, 1)

            pygame.draw.rect(surface, self.__color, self.get_rect())

            if self.glitch_timer <= 0:
                self.glitch_active = False

    def start_glitch(self):
        self.glitch_active = True
        self.glitch_timer = self.glitch_duration
        self.last_glitch_tick = pygame.time.get_ticks()

    def try_dash(self, direction, screenWidth):
        now = pygame.time.get_ticks()
        time_since_last_dash = now - self.last_dash_time

        if not self.dashing and (time_since_last_dash >= self.dash_cooldown) :
            self.dashing = True
            self.returning = False
            self.last_dash_time = now
            if direction == "left":
                if self.__x_coord <= 150:
                    self.dash_target = 0
                else:
                    self.dash_direction = -1
                    self.dash_target = self.__x_coord - self.dash_distance
            elif direction == "right":
                if self.__x_coord >= screenWidth - 150:
                    self.dash_target = screenWidth
                else:
                    self.dash_direction = 1
                    self.dash_target = self.__x_coord + self.dash_distance
            self.start_glitch()
            return True
        return False

    def update_dash(self):
        if self.dashing:
            old_center = (self.__x_coord + self.__width // 2, self.__y_coord + self.__height // 2)

            self.__x_coord += self.dash_speed * self.dash_direction
            
            new_center = (self.__x_coord + self.__width // 2, self.__y_coord + self.__height // 2)
            self.add_trail_segment(old_center, new_center, steps=3)

            if (self.dash_direction == 1 and self.__x_coord >= self.dash_target) or \
               (self.dash_direction == -1 and self.__x_coord <= self.dash_target):
                self.__x_coord = self.dash_target
                self.dashing = False
                self.returning = True

        elif self.returning:
            if (self.dash_direction == 1 and self.__x_coord > self.original_x) or \
               (self.dash_direction == -1 and self.__x_coord < self.original_x):
                self.__x_coord -= self.return_speed * self.dash_direction

                if (self.dash_direction == 1 and self.__x_coord <= self.original_x) or \
                   (self.dash_direction == -1 and self.__x_coord >= self.original_x):
                    self.__x_coord = self.original_x
                    self.returning = False

    def get_dash_cooldown_ratio(self):
        now = pygame.time.get_ticks()
        time_since_dash = now - self.last_dash_time
        return min(time_since_dash / self.dash_cooldown, 1.0)

    def reset(self, x, y):
        self.__x_coord = float(x)
        self.__y_coord = float(y)
        self.glitch_active = False
        self.glitch_timer = 0
        self.last_glitch_tick = 0
        self.returning = False
        self.dashing = False
        self.last_dash_time = 0
        self.original_x = x
        self.dash_direction = 0
        self.trail_positions = []
        self.active_particles = []

    def move(self, dx, dy):
        self.__x_coord += dx
        self.__y_coord += dy

    def add_trail_position(self):
        center = (self.__x_coord + self.__width // 2, self.__y_coord + self.__height // 2)
        if self._just_interpolated:
            self.trail_positions.append(center)
            if len(self.trail_positions) > 60:
                self.trail_positions.pop(0)
            self._just_interpolated = False
        elif self.trail_positions:
            last = self.trail_positions[-1]
            dist = ((center[0] - last[0]) ** 2 + (center[1] - last[1]) ** 2) ** 0.5
            if dist > 5:
                steps = int(dist // 5)
                for i in range(1, steps + 1):
                    interp_x = last[0] + (center[0] - last[0]) * i / steps
                    interp_y = last[1] + (center[1] - last[1]) * i / steps
                    self.trail_positions.append((interp_x, interp_y))
                    if len(self.trail_positions) > 60:
                        self.trail_positions.pop(0)
                    
                    # Particle spawning based on new chance
                    if self.trail and self.trail.name != "None" and random.random() < self.particle_spawn_chance_normal:
                        self.active_particles.append((interp_x, interp_y))
            else:
                self.trail_positions.append(center)
                if len(self.trail_positions) > 60:
                    self.trail_positions.pop(0)
                # Particle spawning for small movements
                if self.trail and self.trail.name != "None" and random.random() < (self.particle_spawn_chance_normal / 2): # Halve chance for small movements
                    self.active_particles.append(center)
        else:
            self.trail_positions.append(center)
            if self.trail and self.trail.name != "None":
                self.active_particles.append(center)

        while len(self.active_particles) > self.max_particles:
            self.active_particles.pop(0)

        self._last_trail_pos = center

    def add_trail_segment(self, old_center, new_center, steps=10):
        for i in range(1, steps + 1):
            interp_x = old_center[0] + (new_center[0] - old_center[0]) * i / steps
            interp_y = old_center[1] + (new_center[1] - old_center[1]) * i / steps
            self.trail_positions.append((interp_x, interp_y))
            if len(self.trail_positions) > 60:
                self.trail_positions.pop(0)
            
            # Particle spawning based on new chance for segments
            if self.trail and self.trail.name != "None" and random.random() < self.particle_spawn_chance_segment:
                self.active_particles.append((interp_x, interp_y))

        while len(self.active_particles) > self.max_particles:
            self.active_particles.pop(0)

        self._last_trail_pos = new_center
        self._just_interpolated = True

    def update_trail_for_scroll(self, scroll_speed):
        self.trail_positions = [
            (x - scroll_speed, y) for (x, y) in self.trail_positions
        ]
        self.active_particles = [
            (x - scroll_speed, y) for (x, y) in self.active_particles
        ]

    # Setters
    def set_x_coord(self, x_coord):
        self.__x_coord = x_coord

    def set_y_coord(self, y_coord):
        self.__y_coord = y_coord

    def set_speed(self, speed):
        self.__speed = speed

    def set_color(self, r, g, b):
        self.__color = (r, g, b)

    def set_width(self, width):
        self.__width = width

    def set_height(self, height):
        self.__height = height
        
    def set_skin(self, skin_name):
        self.skin = next((s for s in skins if s.name == skin_name), None)

    def set_trail(self, trail_name):
        self.trail = next((t for t in trails if t.name == trail_name), None)

    # Getters
    def get_speed(self):
        return self.__speed

    def get_x_coord(self):
        return int(self.__x_coord)

    def get_y_coord(self):
        return int(self.__y_coord)

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height

    def get_color(self):
        return self.__color
    
    