import pygame
import math
import random
from Robot import Robot
from Obstacle import Obstacle, PairedObstacle, MovingObstacle
from Menus import MainMenu, GameOverMenu, Shop
from Coin import Coin, KeyCollectible, GlitchCollectible
from Manager import DataManager, BestTimeManager
from Customisations import skins, trails
from InGameThings import PortalSystem
import os
import sys


if sys.version_info < (3, 7):
    print("Python 3.7+ required!")
    sys.exit(1)

if pygame.version.vernum < (2, 0):
    print("Pygame 2.0+ required!")
    sys.exit(1)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))  # script folder
    return os.path.join(base_path, relative_path)


# Initialize pygame
pygame.init()
screenWidth = 1500
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
pygame.display.set_caption("HACK*LINE")
data_manager = DataManager()
total_score = data_manager.get_coins()
best_time_manager = BestTimeManager()
best_time = best_time_manager.load_longest_time()
shop = Shop(screen, screenWidth, screenHeight, data_manager, skins, trails)
portal_system = PortalSystem(screenWidth, screenHeight)



try:
    hacker_font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 30)

    coin_sound_1 = pygame.mixer.Sound(resource_path("sounds/coin/coin-collect-retro-1.mp3"))
    coin_sound_2 = pygame.mixer.Sound(resource_path("sounds/coin/coin-collect-retro-2.mp3"))
    coin_sound_3 = pygame.mixer.Sound(resource_path("sounds/coin/coin-collect-retro-3.mp3"))
    zap_sound = pygame.mixer.Sound(resource_path("sounds/dash/electric-shock.mp3"))
    music = pygame.mixer.Sound(resource_path("music/unlocked-hacker-mode.mp3"))
    portal_sound = pygame.mixer.Sound(resource_path("sounds/portal/scifi-whoosh.mp3"))
    keycard_sound = pygame.mixer.Sound(resource_path("sounds/portal/keycard.mp3"))

    coin_sound_1.set_volume(0.3)
    coin_sound_2.set_volume(0.3)
    coin_sound_3.set_volume(0.1)
    zap_sound.set_volume(0.3)
    music.set_volume(0.2)
    portal_sound.set_volume(0.2)
    keycard_sound.set_volume(0.3)

except Exception as e:
    print(f"Error loading sounds: {e}")
    hacker_font = pygame.font.SysFont("Courier New", 30, bold=True)
    coin_sound_1 = None
    coin_sound_2 = None
    coin_sound_3 = None
    zap_sound = None
    music = None
    portal_sound = None
    keycard_sound = None


# Colors for the timer
GREEN = (0, 255, 0)  # Classic terminal green
CYAN = (0, 255, 255)  # For glitch effects
DARK_GREY = (20, 20, 20)  # Semi-transparent background
RED = (255, 0, 0)
GREY = (128, 128, 128)

# Game states and menus
main_menu = MainMenu(screen, screenWidth, screenHeight)
game_over_menu = GameOverMenu(screen, screenWidth, screenHeight)
game_state = "main_menu"
final_survival_time = 0
final_score = 0

# Create robot
LANE_COUNT = 3
LANE_Y_POSITIONS = [screenHeight * 0.1, screenHeight * 0.5, screenHeight * 0.9]
robot_lane = 1
robot_starting_x = 400
last_lane_switch = 0
lane_cooldown = 150  # milliseconds between switches
robot = Robot(robot_starting_x, LANE_Y_POSITIONS[1], 20, 20)

# Set skin/trail - ensure we pass strings
skin_name = shop.get_selected_skin() or "None"  # Force string
trail_name = shop.get_selected_trail() or "None"  # Force string

robot.set_skin(skin_name)
robot.set_trail(trail_name)
clock = pygame.time.Clock()


# Load background
bg_path = resource_path(os.path.join("background", "hack.webp"))
bg = pygame.image.load(bg_path)
bg_width = bg.get_width()
bg = pygame.transform.scale(bg, (bg_width, screenHeight))

# Game variables (for background movement)
scroll = 0
tiles = math.ceil(screenWidth/bg_width) + 1

obstacles = []
obstacle_timer = 0
obstacle_spawn_delay = 2000  # milliseconds

coins = []
coin_spawn_timer = 0
coin_spawn_delay = 1000  # 1.5 seconds between coins
score = 0

def draw_hacker_ui(elapsed_seconds, total_score, score, best_time, keys_collected):
    # Smaller font for compact display
    small_hacker_font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 20)
    
    # Base UI elements (always visible)
    timer_text = f"TIME: {int(elapsed_seconds)} SEC"
    best_text = f"BEST TIME: {int(best_time)} SEC"
    score_text = f"TOTAL DATA: {total_score + score} Mb"
    intrusion_text = f"INTRUSION DETECTED!"  # Fixed typo

    # Render base text surfaces
    timer_surface = small_hacker_font.render(timer_text, True, GREEN)
    best_surface = small_hacker_font.render(best_text, True, GREEN)
    score_surface = small_hacker_font.render(score_text, True, GREEN)
    intrusion_surface = hacker_font.render(intrusion_text, True, RED)

    # Calculate base UI box size (without keys)
    base_surfaces = [timer_surface, best_surface, score_surface]
    ui_width = max(s.get_width() for s in base_surfaces) + 2 * 10
    ui_height = (sum(s.get_height() for s in base_surfaces) + 
                (len(base_surfaces) - 1) * 6 + 
                2 * 8)

    # Create and draw base UI
    ui_bg = pygame.Surface((ui_width, ui_height), pygame.SRCALPHA)
    pygame.draw.rect(ui_bg, (*DARK_GREY, 200), (0, 0, ui_width, ui_height), border_radius=5)
    pygame.draw.rect(ui_bg, GREEN, (0, 0, ui_width, ui_height), 1, border_radius=5)

    # Blit base text
    y = 8
    for surface in base_surfaces:
        ui_bg.blit(surface, (10, y))
        y += surface.get_height() + 6

    # Blit to top-right corner
    screen.blit(ui_bg, (screenWidth - ui_width - 10, 10))

    # Only show portal-related UI elements if portal is active
    if portal_system.active:
        # Show intrusion warning
        screen.blit(intrusion_surface, ((screenWidth/2)-150, 10))
        
        # Show key fragments collected (appears below main UI)
        keys_text = f"KEY FRAGMENTS: {keys_collected}/5"
        keys_surface = small_hacker_font.render(keys_text, True, CYAN)
        
        # Create separate UI element for keys
        keys_bg = pygame.Surface((keys_surface.get_width() + 20, keys_surface.get_height() + 16), 
                                pygame.SRCALPHA)
        pygame.draw.rect(keys_bg, (*DARK_GREY, 200), 
                         (0, 0, keys_surface.get_width() + 20, keys_surface.get_height() + 16), 
                         border_radius=5)
        pygame.draw.rect(keys_bg, CYAN, 
                         (0, 0, keys_surface.get_width() + 20, keys_surface.get_height() + 16), 
                         1, border_radius=5)
        keys_bg.blit(keys_surface, (10, 8))
        
        # Position below main UI
        screen.blit(keys_bg, 
                   (screenWidth - keys_surface.get_width() - 20, 
                    ui_height + 20))  # Position below main UI
        


# Game loop
running = True
while running:
    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    
    if game_state == "main_menu":
        game_over_menu.set_stats(final_survival_time, final_score, total_score)
        main_menu.set_total_score(total_score)
        total_score = data_manager.get_coins()
        main_menu.draw()
        
        for event in events:
            clicked_button_index = main_menu.handle_event(event)
            if clicked_button_index is not None:
                if clicked_button_index == 0:  # INITIATE HACK
                    game_state = "playing"
                    key_fragments_collected = 0
                    glitch_coin_pattern_angle = 0
                    key_spawn_timer = 0
                    glitch_spawn_timer = 0
                    start_time = pygame.time.get_ticks()
                    robot_lane = 1  # Middle lane
                    robot.set_y_coord(LANE_Y_POSITIONS[robot_lane])  # Force exact position
                    last_lane_switch = 0  # Reset cooldown timer
                    music.play()
                elif clicked_button_index == 1:  # CONFIGURE SYSTEM
                        game_state = "shop"
                elif clicked_button_index == 2:  # TERMINATE SESSION
                    running = False
    
    elif game_state == "playing":
        current_time = pygame.time.get_ticks() 
        elapsed_time = (current_time - start_time) / 1000  # seconds

        robot_x_coord = robot.get_x_coord()
        robot_y_coord = robot.get_y_coord()

        # Draw scrolling background
        for i in range(0, tiles):
            screen.blit(bg, (i*bg_width + scroll, 0))

        scroll_speed = min(3 + (elapsed_time ** 1.4) * 0.01, 12)
        scroll -= scroll_speed

        if abs(scroll) > bg_width:
            scroll = 0

        if not portal_system.active:
            # Draw lane lines
            pygame.draw.line(screen, (105,105,105), (0, LANE_Y_POSITIONS[0]+10), (screenWidth, LANE_Y_POSITIONS[0]+10), 1)
            pygame.draw.line(screen, (105,105,105), (0, LANE_Y_POSITIONS[1]+10), (screenWidth, LANE_Y_POSITIONS[1]+10), 1)
            pygame.draw.line(screen, (105,105,105), (0, LANE_Y_POSITIONS[2]+10), (screenWidth, LANE_Y_POSITIONS[2]+10), 1)

            if keys[pygame.K_w] and robot_lane > 0 and current_time - last_lane_switch > lane_cooldown and not robot.dashing:
                old_center = (robot.get_x_coord() + robot.get_width() // 2, robot.get_y_coord() + robot.get_height() // 2)
                new_lane = robot_lane - 1
                dy = LANE_Y_POSITIONS[new_lane] - robot.get_y_coord()
                robot.move(0, dy)
                new_center = (robot.get_x_coord() + robot.get_width() // 2, robot.get_y_coord() + robot.get_height() // 2)
                robot.add_trail_segment(old_center, new_center)
                robot_lane = new_lane
                last_lane_switch = current_time
                robot.start_glitch()
                zap_sound.play()

            if keys[pygame.K_s] and robot_lane < LANE_COUNT - 1 and current_time - last_lane_switch > lane_cooldown and not robot.dashing:
                old_center = (robot.get_x_coord() + robot.get_width() // 2, robot.get_y_coord() + robot.get_height() // 2)
                new_lane = robot_lane + 1
                dy = LANE_Y_POSITIONS[new_lane] - robot.get_y_coord()
                robot.move(0, dy)
                new_center = (robot.get_x_coord() + robot.get_width() // 2, robot.get_y_coord() + robot.get_height() // 2)
                robot.add_trail_segment(old_center, new_center)
                robot_lane = new_lane
                last_lane_switch = current_time
                robot.start_glitch()
                zap_sound.play()

            if keys[pygame.K_d]:
                if robot.try_dash("right", screenWidth):
                    zap_sound.play()
            elif keys[pygame.K_a]:
                if robot.try_dash("left", screenWidth):
                    zap_sound.play()

        if portal_system.active:
            if keys[pygame.K_w]:
                robot.move(0, -robot.get_speed())
            if keys[pygame.K_a]:
                robot.move(-robot.get_speed(), 0)
            if keys[pygame.K_s]:
                robot.move(0, robot.get_speed())
            if keys[pygame.K_d]:
                robot.move(robot.get_speed(), 0)

        # Continuous updates (outside the event loop)
        robot.update_dash()
        robot.update_trail_for_scroll(scroll_speed)
        robot.add_trail_position()  # <--- Always add a trail point every frame
        robot.draw(screen)
        
        # Screen boundary checks
        if robot_x_coord < 0:
            robot.set_x_coord(0)
        if robot_x_coord + robot.get_width() > screenWidth:
            robot.set_x_coord(screenWidth - robot.get_width())
        if robot_y_coord < 0:
            robot.set_y_coord(0)
        if robot_y_coord > screenHeight:
            robot.set_y_coord(screenHeight - robot.get_width())

        # Obstacle spawning
        if not portal_system.active:
            portal_system.try_spawn_portal()
            
            obstacle_spawn_delay = max(300, 2000 - int((elapsed_time**1.2) * 5))
            if current_time - obstacle_timer > obstacle_spawn_delay:
                can_spawn = True
                if len(obstacles) > 0:
                    last_obstacle = obstacles[-1]
                    if last_obstacle.get_x_coord() > screenWidth - 150:
                        can_spawn = False

                    last_type = last_obstacle.get_type() if hasattr(last_obstacle, 'get_type') else None

                    # After 50s, allow type 3 (oscillating)
                    available_types = [0, 1, 2]
                    if elapsed_time > 40:
                        if elapsed_time > 80:
                            if elapsed_time > 120:
                                available_types.append(3)
                            available_types.append(3)
                        available_types.append(3)

                    next_type_num = random.choice(available_types)
                    next_type = (
                        "top" if next_type_num == 0 else
                        "bottom" if next_type_num == 1 else
                        "floating" if next_type_num == 2 else
                        "oscillating"
                    )

                    # Prevent top-bottom direct succession
                    if (last_type == "top" and next_type == "bottom") or (last_type == "bottom" and next_type == "top"):
                        can_spawn = False
                else:
                    # First spawn: choose among available types
                    available_types = [0, 1, 2]
                    next_type_num = random.choice(available_types)
                    can_spawn = True

                if can_spawn:
                    obstacle_timer = current_time

                    spawn_chance = random.random()
                    if spawn_chance < 0.65:
                        # Spawn single obstacle
                        if next_type_num == 3:
                            obstacles.append(MovingObstacle(screenWidth, screenHeight))
                        else:
                            obstacles.append(Obstacle(screenWidth, screenHeight, next_type_num))
                    else:
                        # Spawn paired obstacle
                        obstacles.append(PairedObstacle(screenWidth, screenHeight, LANE_Y_POSITIONS))
            
                
        # Obstacle updates and collision
        robot_rect = pygame.Rect(robot_x_coord, robot_y_coord, robot.get_width(), robot.get_height())

        for obstacle in obstacles[:]:
            obstacle.update(scroll_speed)
            obstacle.draw(screen)

            collision_detected = False

            if isinstance(obstacle, PairedObstacle):
                top_rect = obstacle.get_top_rect()
                bottom_rect = obstacle.get_bottom_rect()
                if robot_rect.colliderect(top_rect) or robot_rect.colliderect(bottom_rect):
                    collision_detected = True

            elif isinstance(obstacle, MovingObstacle):
                if robot_rect.colliderect(obstacle.get_rect()):
                    collision_detected = True

            else:
                obstacle_rect = pygame.Rect(
                    obstacle.get_x_coord(), obstacle.get_y_coord(), obstacle.get_width(), obstacle.get_height()
                )
                if robot_rect.colliderect(obstacle_rect):
                    collision_detected = True

            if collision_detected:
                final_survival_time = elapsed_time
                best_time = best_time_manager.update_longest_time(final_survival_time)  # Update & save best time
                final_score = score
                total_score += final_score
                data_manager.set_coins(total_score)
                game_over_menu.set_stats(final_survival_time, final_score, total_score)
                main_menu.set_total_score(total_score)
                game_state = "game_over"

            if obstacle.is_off_screen():
                obstacles.remove(obstacle)


        #checking for portal collision
        entry_rect = portal_system.get_entry_portal_rect()
        if entry_rect and robot_rect.colliderect(entry_rect):
            portal_system.activate(robot, obstacles)
            portal_sound.play()

        exit_rect = portal_system.get_exit_portal_rect()
        if exit_rect and robot_rect.colliderect(exit_rect):
            portal_system.end_effect()
            robot.set_y_coord(LANE_Y_POSITIONS[1])
            robot_lane = 1 
            last_lane_switch = current_time
            key_fragments_collected = 0
            glitch_coin_pattern_angle = 0
            key_spawn_timer = 0
            glitch_spawn_timer = 0
            portal_sound.play()
        
        #checking for virus collisions
        viruses = portal_system.get_viruses()
        for virus in viruses[:]:  # Make a copy with [:] for safe removal
            virus_rect = portal_system.get_virus_rect(virus)  # Your existing get_rect() method works fine
            
            if robot_rect.colliderect(virus_rect):
                # Handle collision effects
                final_survival_time = elapsed_time
                best_time = best_time_manager.update_longest_time(final_survival_time)  # Update & save best time
                final_score = score
                total_score += final_score
                data_manager.set_coins(total_score)
                game_over_menu.set_stats(final_survival_time, final_score, total_score)
                main_menu.set_total_score(total_score)
                game_state = "game_over"

        portal_system.update(robot_x_coord, robot_y_coord, scroll_speed)
        portal_system.draw(screen)


        # Coin spawning outside portal
        if not portal_system.player_inside:
            if current_time - coin_spawn_timer > coin_spawn_delay:
                coin_spawn_timer = current_time

                potential_coin_x = screenWidth + random.randint(0, 50)
                potential_coin_y = random.choice(LANE_Y_POSITIONS)
                
                dummy_coin = Coin(potential_coin_x, potential_coin_y, current_time)
                potential_coin_rect = dummy_coin.get_rect()

                can_spawn_coin = True
                for obstacle in obstacles:
                    # Check if the obstacle is an instance of PairedObstacle (replace 'PairedObstacle' if your class name is different)
                    # This requires the PairedObstacle class to be imported or defined in the same scope.
                    if hasattr(obstacle, 'obstacle_top') and hasattr(obstacle, 'obstacle_bottom') and \
                    callable(getattr(obstacle, 'obstacle_top').get_rect) and callable(getattr(obstacle, 'obstacle_bottom').get_rect):
                        # If it looks like a PairedObstacle with top/bottom components
                        if potential_coin_rect.colliderect(obstacle.obstacle_top.get_rect()) or \
                        potential_coin_rect.colliderect(obstacle.obstacle_bottom.get_rect()):
                            can_spawn_coin = False
                            break
                    else:
                        # For regular (non-paired) obstacles, or if PairedObstacle structure is different,
                        # assume it directly has a get_rect() method.
                        # You might need to add a try-except block here for robustness if other obstacles
                        # might also lack get_rect().
                        if hasattr(obstacle, 'get_rect') and callable(obstacle.get_rect):
                            if potential_coin_rect.colliderect(obstacle.get_rect()):
                                can_spawn_coin = False
                                break
                        # else:
                        #     # If an obstacle doesn't have a get_rect, you might want to log a warning
                        #     # or handle it as an error, depending on your game design.
                        #     print(f"Warning: Obstacle {obstacle} does not have a get_rect() method and is not a recognized PairedObstacle structure.")


                if can_spawn_coin:
                    coins.append(Coin(potential_coin_x, potential_coin_y, current_time))

        
        # Coin spawning inside portal
        if portal_system.player_inside:
            # Spawn key fragments
            if (key_fragments_collected < 5 and 
                current_time - key_spawn_timer > KeyCollectible.SPAWN_DELAY):
                
                key_spawn_timer = current_time
                key_x = screenWidth + random.randint(0, 100)
                key_y = random.randint(100, screenHeight - 100)
                
                if KeyCollectible.can_spawn(key_x, key_y, obstacles):
                    coins.append(KeyCollectible(key_x, key_y, current_time))

            # Spawn glitch pattern
            if current_time - glitch_spawn_timer > GlitchCollectible.SPAWN_DELAY:
                glitch_spawn_timer = current_time
                
                glitch_center_x = screenWidth + 100
                glitch_center_y = screenHeight // 2
                
                if GlitchCollectible.can_spawn_pattern(glitch_center_x, glitch_center_y, obstacles):
                    for i in range(GlitchCollectible.PATTERN_COUNT):
                        angle = glitch_coin_pattern_angle + i * (360 / GlitchCollectible.PATTERN_COUNT)
                        rad = math.radians(angle)
                        gx = glitch_center_x + GlitchCollectible.PATTERN_RADIUS * math.cos(rad)
                        gy = glitch_center_y + GlitchCollectible.PATTERN_RADIUS * math.sin(rad)
                        coins.append(GlitchCollectible(gx, gy, current_time))
                    
                    glitch_coin_pattern_angle = (glitch_coin_pattern_angle + 15) % 360


        # === Coin updates and collection (should run in ALL cases) ===
        for coin in coins[:]:
            if isinstance(coin, (KeyCollectible, GlitchCollectible)):
                coin.update(scroll_speed)  # For portal collectibles
            else:
                coin.update(scroll_speed, current_time)

            if not coin.collected and robot_rect.colliderect(coin.get_rect()):
                score += coin.collect()

                if coin.type == "DATA":
                    coin_sound_1.play()
                elif coin.type == "CRYPTO":
                    coin_sound_2.play()
                elif coin.type == "BITCOIN":
                    coin_sound_3.play()
                elif coin.type == "KEY":
                    keycard_sound.play()
                    key_fragments_collected += 1
                    if key_fragments_collected >= 5:
                        portal_system.spawn_exit_portal()
                elif coin.type == "GLITCH":
                    coin_sound_2.play()

            if coin.x < -coin.size or coin.collected:
                coins.remove(coin)

        # === Draw coins (also in all cases) ===
        for coin in coins:
            if (portal_system.player_inside and coin.type not in ["DATA", "CRYPTO", "BITCOIN"]) or \
                (not portal_system.player_inside and coin.type not in ["KEY", "GLITCH"]):
                    coin.draw(screen)
            

        # Dash cooldown UI
        bar_width, bar_height = 100, 10
        bar_x, bar_y = 20, 20

        cooldown_ratio = robot.get_dash_cooldown_ratio()
        filled_width = int(bar_width * cooldown_ratio)

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        color = (0, 255, 0) if cooldown_ratio >= 1.0 else (255, 0, 0)
        pygame.draw.rect(screen, color, (bar_x, bar_y, filled_width, bar_height))

        # Draw hacker-style timer and score
        draw_hacker_ui(elapsed_time, total_score, score, best_time, key_fragments_collected)
        
        pygame.display.flip()

    elif game_state == "game_over":
        game_over_menu.draw()
        music.stop()
        
        clicked_retry = False
        for event in events:
            if game_over_menu.handle_event(event):
                clicked_retry = True
        
        if clicked_retry or game_over_menu.handle_input(keys):
            # Reset for new game
            portal_system.end_effect()
            robot.reset(robot_starting_x, LANE_Y_POSITIONS[1])
            robot.set_skin(data_manager.get_equipped_skin())
            robot.set_trail(data_manager.get_equipped_trail())
            obstacles.clear()
            coins.clear()
            scroll = 0
            obstacle_timer = pygame.time.get_ticks()
            coin_spawn_timer = pygame.time.get_ticks()
            start_time = pygame.time.get_ticks()
            score = 0
            game_state = "main_menu"  # or "playing" if you want immediate restart

    elif game_state == "shop":
        shop.draw()

        for event in events:  # 'events' is presumably from pygame.event.get() earlier
            result = shop.handle_event(event)
            if result == "back" or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                game_state = "main_menu"
                
        robot.set_skin(shop.get_selected_skin())
        robot.set_trail(shop.get_selected_trail())
        pygame.display.flip()

    clock.tick(60)

pygame.quit()