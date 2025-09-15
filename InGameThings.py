import pygame
import random
import math

class Virus:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.base_radius = 15
        self.radius = self.base_radius
        self.speed = 2
        self.target_x = target_x
        self.target_y = target_y
        self.base_color = (255, 50, 50)  # Core red color
        self.pulse_timer = 0
        self.rotation_angle = 0
        self.spikes = random.randint(6, 10)  # Random number of spikes
        self.spike_length = random.uniform(1.2, 1.5)  # Spike length multiplier
        self.inner_circle_ratio = 0.6  # Inner circle size ratio
        self.particle_trail = []
        self.max_particles = 15
        
    def update(self, scroll_speed, x_coord, y_coord):
        # Store previous position for particle trail
        prev_x, prev_y = self.x, self.y
        
        # Move toward player with magnet effect
        dx = x_coord - self.x
        dy = y_coord - self.y
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        
        self.x += (dx / distance) * self.speed*0.4
        self.y += (dy / distance) * (self.speed + (scroll_speed*0.1)**1.5) 
        
        # Scroll with background
        self.x -= scroll_speed
        
        # Update effects
        self.pulse_timer += 0.1
        self.rotation_angle += 0.02
        self.radius = self.base_radius + 2 * math.sin(self.pulse_timer)
        
        # Add particle to trail
        if random.random() < 0.3:  # 30% chance to add particle each frame
            self.particle_trail.append({
                'x': prev_x,
                'y': prev_y,
                'size': random.randint(2, 4),
                'life': random.randint(20, 30)
            })
        
        # Update and cull particles
        self.particle_trail = [p for p in self.particle_trail if p['life'] > 0]
        for p in self.particle_trail:
            p['life'] -= 1
            p['x'] -= scroll_speed * 0.5  # Particles move slower than virus
            
        # Keep trail from growing too long
        if len(self.particle_trail) > self.max_particles:
            self.particle_trail.pop(0)
            
    def draw(self, screen):
        # Draw particle trail first (behind virus)
        for p in self.particle_trail:
            alpha = int(255 * (p['life'] / 30))
            color = (255, 100, 100, alpha)
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), p['size'])
        
        # Draw pulsing glow effect
        glow_radius = self.radius + 8 * math.sin(self.pulse_timer * 0.5)
        glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 50, 50, 50), 
                          (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (int(self.x - glow_radius), int(self.y - glow_radius)))
        
        # Draw main virus body
        pygame.draw.circle(screen, self.base_color, (int(self.x), int(self.y)), self.radius)
        
        # Draw inner circle (darker core)
        inner_color = (200, 30, 30)
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), 
                         self.radius * self.inner_circle_ratio)
        
        # Draw spikes
        spike_angle = 2 * math.pi / self.spikes
        for i in range(self.spikes):
            angle = self.rotation_angle + i * spike_angle
            # Base of spike
            x1 = self.x + math.cos(angle) * self.radius * 0.8
            y1 = self.y + math.sin(angle) * self.radius * 0.8
            # Tip of spike
            x2 = self.x + math.cos(angle) * self.radius * self.spike_length
            y2 = self.y + math.sin(angle) * self.radius * self.spike_length
            
            pygame.draw.line(screen, (255, 100, 100), (x1, y1), (x2, y2), 2)
        
        # Draw pulsing outline
        outline_width = 1 + math.sin(self.pulse_timer)
        pygame.draw.circle(screen, (255, 150, 150), (int(self.x), int(self.y)), 
                         self.radius + 3, int(outline_width))
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                         self.radius * 2, self.radius * 2)

class Portal:
    def __init__(self, x, is_entry=True):
        self.x = x
        self.width = 50
        self.animation_frame = 0
        self.is_entry = is_entry
        self.active = True
    
    def update(self, scroll_speed):
        self.animation_frame = (self.animation_frame + 0.2) % 10
        self.x -= scroll_speed
        
    def draw(self, screen):

        if not self.active:
            return
            
        color = (0, 200, 255) if self.is_entry else (255, 150, 0)
        alpha = 150 + int(50 * math.sin(self.animation_frame))
        
        # Full height portal
        portal_height = screen.get_height()
        portal_surface = pygame.Surface((self.width, portal_height), pygame.SRCALPHA)
        pygame.draw.rect(portal_surface, (*color, alpha), 
                        (0, 0, self.width, portal_height))
        screen.blit(portal_surface, (self.x, 0))
        
    def get_rect(self, screen_height):
        return pygame.Rect(self.x, 0, self.width, screen_height)

class PortalSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.entry_portal = None
        self.exit_portal = None
        self.viruses = []
        self.active = False
        self.portal_timer = 0
        self.portal_duration = 8000  # Max duration as fallback
        self.player_inside = False
        self.awaiting_exit = False  # New state flag
        self.last_spawn_time = 0
        self.spawn_cooldown = 1000

    def try_spawn_portal(self):
        if not self.active and self.entry_portal == None and random.random() < 0.001:
            self.entry_portal = Portal(self.screen_width, True)
            return True
        return False
        
    def activate(self, player, obstacles):
        self.active = True
        self.awaiting_exit = True  # Player must use exit portal
        self.portal_timer = pygame.time.get_ticks()
        self.player_inside = True
        
        # Start breaking all existing obstacles
        for obstacle in obstacles[:]:
            if hasattr(obstacle, 'start_breaking'):
                obstacle.start_breaking()
            obstacles.remove(obstacle)  # Remove immediately
            
        
            
    
            
    def update(self, x_coord, y_coord, scroll_speed):

          # Update portals
        if self.entry_portal:
            scroll_speed = scroll_speed * 1.5 if self.player_inside else scroll_speed
            self.entry_portal.update(scroll_speed)
        if self.exit_portal:
            self.exit_portal.update(scroll_speed)
            
        if not self.active:
            return
            
            
        # Update viruses
        for virus in self.viruses[:]:
            virus.update(scroll_speed, x_coord, y_coord)
            if virus.x < -50:  # Remove off-screen viruses
                self.viruses.remove(virus)
                
        # Spawn new viruses occasionally
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_spawn_time > max((300, self.spawn_cooldown-(scroll_speed**2)))):
            self.spawn_virus(x_coord, y_coord)
            self.last_spawn_time = current_time
            
    def end_effect(self):
        self.active = False
        self.awaiting_exit = False
        self.entry_portal = None
        self.exit_portal = None
        self.player_inside = False
        self.viruses = []
        
    def draw(self, screen):
        if self.entry_portal:
            self.entry_portal.draw(screen)
        if self.exit_portal:
            self.exit_portal.draw(screen)
        for virus in self.viruses:
            virus.draw(screen)

    def get_entry_portal_rect(self):
        if self.entry_portal:
            return self.entry_portal.get_rect(self.screen_height)
        return None

    def get_exit_portal_rect(self):
        if self.exit_portal:
            return self.exit_portal.get_rect(self.screen_height)
        return None
    
    def get_virus_rect(self, virus):
        return virus.get_rect()
    
    def get_viruses(self):
        return self.viruses
    
    
    def spawn_virus(self, target_x, target_y):
        """Create a new virus targeting the player's position"""
        new_virus = Virus(
            x=self.screen_width + random.randint(50, 200),  # Spawn off-screen right
            y=random.randint(50, self.screen_height - 50),  # Random vertical position
            target_x=target_x,
            target_y=target_y
        )
        self.viruses.append(new_virus)
        return new_virus

    def spawn_exit_portal(self):
        """Force spawn the exit portal early if conditions are met."""
        if self.awaiting_exit and not self.exit_portal:
            self.exit_portal = Portal(self.screen_width, is_entry=False)