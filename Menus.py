import pygame
import random
import time
from Buttons import HackerButton
from Manager import BestTimeManager
import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))  # script folder
    return os.path.join(base_path, relative_path)

class MainMenu:
    def __init__(self, screen, screenWidth, screenHeight):
        self.screen = screen
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.total_data = 0

        # Hacker theme colors
        self.primary_color = (0, 255, 0)
        self.secondary_color = (0, 200, 255)
        self.error_color = (255, 50, 50)

        # Load fonts
        try:
            self.title_font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 64)
            self.subtitle_font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 24)
        except:
            self.title_font = pygame.font.SysFont("Courier New", 64, bold=True)
            self.subtitle_font = pygame.font.SysFont("Courier New", 24, bold=True)

        # Create buttons
        button_width = 400
        self.buttons = [
            HackerButton(screenWidth // 2 - button_width // 2, screenHeight // 2 - 60,
                         button_width, 50, "INITIATE HACK", self.primary_color),
            HackerButton(screenWidth // 2 - button_width // 2, screenHeight // 2 + 20,
                         button_width, 50, "CONFIGURE SYSTEM", self.secondary_color),
            HackerButton(screenWidth // 2 - button_width // 2, screenHeight // 2 + 100,
                         button_width, 50, "TERMINATE SESSION", self.error_color)
        ]

        # Matrix rain setup
        self.matrix_chars_set = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZｱｲｳエオカキクケコサシスセソタチツテトﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
        self.matrix_drops = []
        self.init_matrix_rain()

        # Terminal boot animation
        self.boot_messages = [
            "> INITIALIZING HACKER PROTOCOLS",
            "> CONNECTING TO MAINFRAME",
            "> BYPASSING SECURITY",
            "> SYSTEM ACCESS GRANTED"
        ]
        self.current_message = 0
        self.message_timer = 0
        self.boot_complete = False

    def _generate_drop_characters(self, length):
        """Generates a sequence of characters for a single matrix drop."""
        return [random.choice(self.matrix_chars_set) for _ in range(length)]

    def init_matrix_rain(self):
        """Initializes matrix rain drops for a continuous vertical flow."""
        matrix_font_size = self.subtitle_font.get_height()
        for x in range(0, self.screenWidth, 20):
            length = random.randint(25, 50)
            initial_y = random.randint(-self.screenHeight * 2, -matrix_font_size * 5)
            
            self.matrix_drops.append({
                'x': x,
                'y': initial_y,
                'speed': random.uniform(1.5, 3.5), # Decreased speed range further
                'length': length,
                'characters': self._generate_drop_characters(length)
            })

    def update_matrix_rain(self):
        matrix_font_size = self.subtitle_font.get_height()
        for drop in self.matrix_drops:
            drop['y'] += drop['speed']
            
            if drop['y'] > self.screenHeight:
                drop['length'] = random.randint(25, 50)
                drop['y'] = - (drop['length'] * matrix_font_size) - random.randint(0, self.screenHeight // 4)
                drop['speed'] = random.uniform(1.5, 3.5) # Decreased speed range further
                drop['characters'] = self._generate_drop_characters(drop['length'])

            if random.random() < 0.05:
                idx = random.randint(0, drop['length'] - 1)
                drop['characters'][idx] = random.choice(self.matrix_chars_set)

    def draw_matrix_rain(self):
        matrix_font_size = self.subtitle_font.get_height()

        for drop in self.matrix_drops:
            for i in range(drop['length']):
                alpha = max(0, 255 - int(255 * (i / drop['length'])))
                
                char = drop['characters'][i]

                y_pos = drop['y'] + i * matrix_font_size

                if 0 <= y_pos < self.screenHeight:
                    base_green_intensity = 180
                    g_component = max(0, min(255, base_green_intensity - int(i * (base_green_intensity / drop['length']))))
                    color = (0, g_component, 0)
                    
                    char_surface = self.subtitle_font.render(char, True, color)
                    char_surface.set_alpha(alpha)
                    self.screen.blit(char_surface, (drop['x'], y_pos))

    def draw_gradient_background(self):
        """Draw a vertical green-to-black gradient background"""
        for y in range(self.screenHeight):
            g = max(0, 50 - y // 4)
            color = (0, g, 0)
            pygame.draw.line(self.screen, color, (0, y), (self.screenWidth, y))

    def draw_grid_overlay(self):
        """Optional HUD-style grid"""
        grid_color = (0, 30, 0)
        for x in range(0, self.screenWidth, 80):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.screenHeight))
        for y in range(0, self.screenHeight, 80):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.screenWidth, y))

    def draw_scanline_flicker(self):
        """Occasional flicker line"""
        if random.random() < 0.002:
            y = random.randint(0, self.screenHeight)
            pygame.draw.line(self.screen, (0, 100, 0), (0, y), (self.screenWidth, y), 1)

    def draw_boot_sequence(self):
        if self.boot_complete:
            return

        self.message_timer += 1
        if self.message_timer > 60 and self.current_message < len(self.boot_messages):
            self.current_message += 1
            self.message_timer = 0

        if self.current_message >= len(self.boot_messages):
            self.boot_complete = True

        cursor_blink = time.time() % 1 > 0.5

        for i in range(min(self.current_message + 1, len(self.boot_messages))):
            msg = self.boot_messages[i]
            if i == self.current_message and not self.boot_complete and cursor_blink:
                msg += "_"
            else:
                msg += " "
            text_surface = self.subtitle_font.render(msg, True, (0, 200, 0))
            self.screen.blit(text_surface, (50, self.screenHeight - 150 + i * 30))

    def draw(self):
        # Background setup
        self.draw_gradient_background()
        self.update_matrix_rain()
        self.draw_matrix_rain()
        self.draw_grid_overlay()
        self.draw_scanline_flicker()

        # Title
        title_text = self.title_font.render("HACK*LINE", True, self.primary_color)
        title_rect = title_text.get_rect(center=(self.screenWidth // 2, self.screenHeight // 4))

        # Draw a prominent neon blue outline for the title text
        outline_color = self.secondary_color
        outline_thickness = 2
        for dx in range(-outline_thickness, outline_thickness + 1):
            for dy in range(-outline_thickness, outline_thickness + 1):
                if dx != 0 or dy != 0:
                    outline_surface = self.title_font.render("HACK*LINE", True, outline_color)
                    self.screen.blit(outline_surface, (title_rect.x + dx, title_rect.y + dy))

        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_text = self.subtitle_font.render("SYSTEM INTRUSION PROTOCOL", True, self.secondary_color)
        subtitle_rect = subtitle_text.get_rect(center=(self.screenWidth // 2, self.screenHeight // 4 + 70))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Buttons
        for button in self.buttons:
            button.draw(self.screen)

        # Boot messages
        self.draw_boot_sequence()

        # Draw total score if available
        score_text = self.subtitle_font.render(f"TOTAL DATA: {self.total_data} Mb", True, self.primary_color)
        score_rect = score_text.get_rect(center=(self.screenWidth // 2, self.screenHeight - 80))
        self.screen.blit(score_text, score_rect)

        pygame.display.flip()

    def handle_event(self, event):
        for button in self.buttons:
            if button.check_click(event):
                return self.buttons.index(button)
        return None

    def handle_input(self, keys):
        return keys[pygame.K_SPACE]
    
    def set_total_score(self, total_data):
        self.total_data = total_data


class GameOverMenu:
    def __init__(self, screen, screenWidth, screenHeight):
        self.screen = screen
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        best_time_manager = BestTimeManager()
        self.current_best_time = best_time_manager.load_longest_time()

        self.error_color = (255, 50, 50)
        self.warning_color = (255, 150, 0)

        try:
            self.title_font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 48)
            self.stats_font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 24)
            self.button_font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 32)
        except:
            self.title_font = pygame.font.SysFont("Courier New", 48, bold=True)
            self.stats_font = pygame.font.SysFont("Courier New", 24, bold=True)
            self.button_font = pygame.font.SysFont("Courier New", 32, bold=True)

        self.retry_button = HackerButton(
            screenWidth // 2 - 150, screenHeight // 2 + 100,
            300, 50, "REINITIATE HACK", self.warning_color
        )

        self.stats = {'time_survived': 0, 'data_collected': 0}

    def set_stats(self, time, score, total_score):
        self.stats = {
            'time_survived': time,
            'data_collected': score,
            'total_data' : total_score
        }

    def draw(self):
        self.screen.fill((10, 5, 5))

        title_text = self.title_font.render("SYSTEM INTRUSION DETECTED", True, self.error_color)
        title_rect = title_text.get_rect(center=(self.screenWidth // 2, self.screenHeight // 4))
        self.screen.blit(title_text, title_rect)

        stats_y = self.screenHeight // 2 - 80
        for label, value in self.stats.items():
            label_text = label.replace('_', ' ').upper()

            # Add units based on label type
            if 'time' in label:
                if value > self.current_best_time:
                    display_value = f"{value} sec  *NEW BEST TIME!*"
                else:
                    display_value = f"{value} sec"
            elif 'data' in label:
                display_value = f"{value} Mb"
            else:
                display_value = str(value)

            stat_text = self.stats_font.render(f"> {label_text}: {display_value}", True, (200, 200, 200))
            self.screen.blit(stat_text, (self.screenWidth // 2 - 150, stats_y))
            stats_y += 40

        self.retry_button.draw(self.screen)

        continue_text = self.stats_font.render(
            "PRESS [Esc] TO exit OR CLICK COMMAND ABOVE",
            True, (100, 100, 100)
        )
        continue_rect = continue_text.get_rect(center=(self.screenWidth // 2, self.screenHeight - 50))
        self.screen.blit(continue_text, continue_rect)

        pygame.display.flip()

    def handle_event(self, event):
        return self.retry_button.check_click(event)

    def handle_input(self, keys):
        return keys[pygame.K_ESCAPE]
    
class Shop:
    def __init__(self, screen, width, height, data_manager, skins, trails):
        self.screen = screen
        self.width = width
        self.height = height
        self.data_manager = data_manager
        self.skins = skins
        self.trails = trails

        # Hacker style colors
        try: # Try to load retro font, fallback to system font
            self.font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 20)
            self.large_font = pygame.font.Font(resource_path("fonts/Retro/Perfect DOS VGA 437.ttf"), 28) # Larger font for section titles
        except:
            self.font = pygame.font.SysFont("Courier New", 20, bold=True)
            self.large_font = pygame.font.SysFont("Courier New", 28, bold=True)


        self.neon_green = (0, 255, 0)
        self.neon_blue = (0, 200, 255) # Adjusted slightly for contrast
        self.bg_color = (10, 20, 10)
        self.gray = (40, 60, 40)
        self.dark_gray = (20, 30, 20)
        self.light_green = (100, 255, 100) # Used for equip button
        self.error_color = (255, 50, 50) # <--- ADDED THIS LINE

        self.selected_skin = 'default_robot'
        self.selected_trail = 'default_trail'

        # Tabs
        self.tabs = ["Customize", "Shop"]
        self.current_tab = "Customize"
        self.sub_tabs = {"Customize": ["Skin", "Trail"], "Shop": ["Skin", "Trail"]}
        self.current_sub_tab = {"Customize": "Skin", "Shop": "Skin"}

        self.tab_rects = []
        self.sub_tab_rects = []

        self.scroll_offset = 0
        self.target_scroll_offset = 0
        self.scroll_speed = 40

        self.back_button = pygame.Rect(50, self.height - 70, 120, 40)
        self.scroll_up_btn = pygame.Rect(self.width - 60, 150, 40, 40)
        self.scroll_down_btn = pygame.Rect(self.width - 60, 400, 40, 40)

        self.grid_cols = 3
        self.cell_width = 300
        self.cell_height = 300
        self.cell_margin = 20
        self.visible_rows = 1

        self.hovered_cell = None
        self.hovered_button = None
        self.show_not_enough_data = False
        self.not_enough_data_ok_rect = None

    def get_items(self, category):
        if category == "Skin":
            return self.skins
        elif category == "Trail":
            return self.trails
        return []

    def draw(self):
        self.screen.fill(self.bg_color)
        self.tab_rects.clear()
        self.sub_tab_rects.clear()
        mouse_pos = pygame.mouse.get_pos()

        # Draw main tabs
        main_tab_width = 160
        main_tab_height = 50
        tab_y = 10
        padding = 15

        for i, tab in enumerate(self.tabs):
            x = padding + i * (main_tab_width + padding)
            rect = pygame.Rect(x, tab_y, main_tab_width, main_tab_height)
            is_active = (tab == self.current_tab)
            is_hovered = rect.collidepoint(mouse_pos)

            # Active Tab: Neon Blue fill, Black text, Neon Green border
            # Inactive Tab: Dark Gray fill, Neon Green text, Gray border
            fill_color = self.neon_blue if is_active else self.dark_gray
            text_color = self.bg_color if is_active else self.neon_green
            border_color = self.neon_green if is_active else self.gray

            pygame.draw.rect(self.screen, fill_color, rect, border_radius=12)
            
            # Hover effect for all tabs: Thicker/brighter border
            border_thickness = 5 if is_hovered else 3
            pygame.draw.rect(self.screen, border_color, rect, border_thickness, border_radius=12)

            text = self.font.render(tab, True, text_color)
            self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
            self.tab_rects.append((rect, tab))

        # Draw sub-tabs
        sub_tab_width = 120
        sub_tab_height = 35
        sub_tab_y = tab_y + main_tab_height + 15

        for j, sub_tab in enumerate(self.sub_tabs[self.current_tab]):
            x = padding + j * (sub_tab_width + padding)
            rect = pygame.Rect(x, sub_tab_y, sub_tab_width, sub_tab_height)
            is_active = (sub_tab == self.current_sub_tab[self.current_tab])
            is_hovered = rect.collidepoint(mouse_pos)

            # Active Sub-Tab: Neon Blue fill, Black text, Neon Green border
            # Inactive Sub-Tab: Gray fill, Neon Green text, Gray border
            fill_color = self.neon_blue if is_active else self.gray
            text_color = self.bg_color if is_active else self.neon_green
            border_color = self.neon_green if is_active else self.dark_gray

            pygame.draw.rect(self.screen, fill_color, rect, border_radius=8)
            border_thickness = 3 if is_hovered else 2
            pygame.draw.rect(self.screen, border_color, rect, border_thickness, border_radius=8)
            
            text = self.font.render(sub_tab, True, text_color)
            self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
            self.sub_tab_rects.append((rect, sub_tab))

        # Section Title for grid
        section_title_text = f"{self.current_tab.upper()} {self.current_sub_tab[self.current_tab].upper()}"
        section_title_surf = self.large_font.render(section_title_text, True, self.neon_green)
        section_title_rect = section_title_surf.get_rect(center=(self.width // 2, sub_tab_y + sub_tab_height + 30))
        self.screen.blit(section_title_surf, section_title_rect)


        # Draw back button
        back_btn_color = self.neon_green if self.back_button.collidepoint(mouse_pos) else self.gray
        pygame.draw.rect(self.screen, back_btn_color, self.back_button, 0, border_radius=8)
        pygame.draw.rect(self.screen, self.neon_green, self.back_button, 3, border_radius=8)
        back_text = self.font.render("BACK", True, self.bg_color if self.back_button.collidepoint(mouse_pos) else self.neon_green)
        self.screen.blit(back_text, (self.back_button.x + 25, self.back_button.y + 7))

        # Draw scroll buttons
        scroll_btn_base_color = self.dark_gray
        scroll_btn_hover_color = self.neon_blue

        # Up button
        up_btn_fill = scroll_btn_hover_color if self.scroll_up_btn.collidepoint(mouse_pos) else scroll_btn_base_color
        pygame.draw.rect(self.screen, up_btn_fill, self.scroll_up_btn, 0, border_radius=4)
        pygame.draw.rect(self.screen, self.neon_green, self.scroll_up_btn, 2, border_radius=4)
        pygame.draw.polygon(self.screen, self.neon_green, [
            (self.scroll_up_btn.centerx, self.scroll_up_btn.top + 10),
            (self.scroll_up_btn.left + 10, self.scroll_up_btn.bottom - 10),
            (self.scroll_up_btn.right - 10, self.scroll_up_btn.bottom - 10),
        ])

        # Down button
        down_btn_fill = scroll_btn_hover_color if self.scroll_down_btn.collidepoint(mouse_pos) else scroll_btn_base_color
        pygame.draw.rect(self.screen, down_btn_fill, self.scroll_down_btn, 0, border_radius=4)
        pygame.draw.rect(self.screen, self.neon_green, self.scroll_down_btn, 2, border_radius=4)
        pygame.draw.polygon(self.screen, self.neon_green, [
            (self.scroll_down_btn.centerx, self.scroll_down_btn.bottom - 10),
            (self.scroll_down_btn.left + 10, self.scroll_down_btn.top + 10),
            (self.scroll_down_btn.right - 10, self.scroll_down_btn.top + 10),
        ])


        # --- GRID CLIPPING ---
        category = self.current_sub_tab[self.current_tab]
        coins = self.data_manager.get_coins()
        owned_key = "owned_" + category.lower() + "s"
        equipped_key = "equipped_" + category.lower()
        owned_list = getattr(self.data_manager, f"get_{owned_key}")()
        equipped_id = getattr(self.data_manager, f"get_{equipped_key}")()
        all_items = self.get_items(category)

        if self.current_tab == "Shop":
            display_items = [item for item in all_items if item.name not in owned_list]
        else:
            display_items = [item for item in all_items if item.name in owned_list]

        start_x = (self.width - (self.grid_cols * (self.cell_width + self.cell_margin) - self.cell_margin)) // 2
        start_y = section_title_rect.bottom + 15
        
        grid_w = self.grid_cols * (self.cell_width + self.cell_margin) - self.cell_margin
        grid_h = self.visible_rows * (self.cell_height + self.cell_margin) - self.cell_margin
        grid_viewport_rect = pygame.Rect(start_x - 10, start_y - 10, grid_w + 20, grid_h + 20)

        # Grid background and shadow
        shadow_offset = 8
        shadow_color = (0, 0, 0, 100)
        pygame.draw.rect(self.screen, shadow_color, grid_viewport_rect.move(shadow_offset, shadow_offset), border_radius=16)
        pygame.draw.rect(self.screen, self.dark_gray, grid_viewport_rect, border_radius=16)
        pygame.draw.rect(self.screen, self.neon_blue, grid_viewport_rect, 4, border_radius=16)


        # Create grid surface for clipping
        grid_surface = pygame.Surface((grid_viewport_rect.width, grid_viewport_rect.height), pygame.SRCALPHA)
        grid_surface = grid_surface.convert_alpha()

        # --- SCROLLBAR CALC ---
        total_rows = (len(display_items) + self.grid_cols - 1) // self.grid_cols
        content_height = total_rows * (self.cell_height + self.cell_margin)
        visible_viewport_height = self.visible_rows * (self.cell_height + self.cell_margin) - self.cell_margin

        max_scroll = max(0, content_height - visible_viewport_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        # --- SMOOTH SCROLLING ---
        if abs(self.scroll_offset - self.target_scroll_offset) > 1:
            self.scroll_offset += (self.target_scroll_offset - self.scroll_offset) * 0.2
        else:
            self.scroll_offset = self.target_scroll_offset

        # --- DRAW GRID ITEMS ---
        self.hovered_cell = None
        self.hovered_button = None

        for i, item in enumerate(display_items):
            col = i % self.grid_cols
            row = i // self.grid_cols
            x = 10 + col * (self.cell_width + self.cell_margin)
            y = 10 + row * (self.cell_height + self.cell_margin) - self.scroll_offset

            if y + self.cell_height < 0 or y > grid_surface.get_height():
                continue

            cell_rect = pygame.Rect(x, y, self.cell_width, self.cell_height)
            cell_screen_rect = cell_rect.move(grid_viewport_rect.x, grid_viewport_rect.y)
            
            if cell_screen_rect.collidepoint(mouse_pos):
                self.hovered_cell = i
                pygame.draw.rect(grid_surface, self.gray, cell_rect, border_radius=12)
                pygame.draw.rect(grid_surface, self.neon_green, cell_rect, 4, border_radius=14)
            else:
                pygame.draw.rect(grid_surface, self.dark_gray, cell_rect, border_radius=12)
                pygame.draw.rect(grid_surface, self.gray, cell_rect, 2, border_radius=12)

            # Draw preview
            preview_width = int(self.cell_width * 0.6)
            preview_height = int(self.cell_height * 0.6)
            preview_x = x + (self.cell_width - preview_width) // 2
            preview_y = y + 10
            preview_rect = pygame.Rect(preview_x, preview_y, preview_width, preview_height)
            item.draw_preview(grid_surface, preview_rect)

            # Button and label
            padding_bottom = 15
            btn_width = 120
            btn_height = 30
            btn_x = x + (self.cell_width - btn_width) // 2
            btn_y = y + self.cell_height - btn_height - padding_bottom
            btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

            name_surf = self.font.render(item.name, True, self.neon_green)
            name_x = x + (self.cell_width - name_surf.get_width()) // 2
            name_y = btn_y - name_surf.get_height() - 5
            grid_surface.blit(name_surf, (name_x, name_y))

            btn_screen_rect = btn_rect.move(grid_viewport_rect.x, grid_viewport_rect.y)
            is_button_hovered = btn_screen_rect.collidepoint(mouse_pos)
            if is_button_hovered:
                self.hovered_button = (i, item)

            # Button drawing logic
            if item.name in owned_list:
                if equipped_id == item.name:
                    equipped_surf = self.font.render("EQUIPPED", True, self.neon_blue)
                    equipped_rect = equipped_surf.get_rect(center=btn_rect.center)
                    pygame.draw.rect(grid_surface, self.dark_gray, btn_rect, 0, border_radius=8)
                    pygame.draw.rect(grid_surface, self.neon_blue, btn_rect, 2, border_radius=8)
                    grid_surface.blit(equipped_surf, equipped_rect)
                else:
                    button_fill_color = self.neon_green if is_button_hovered else self.light_green
                    button_text_color = self.bg_color if is_button_hovered else self.bg_color # FIX: Changed text color to bg_color
                    pygame.draw.rect(grid_surface, button_fill_color, btn_rect, 0, border_radius=8)
                    pygame.draw.rect(grid_surface, self.neon_green, btn_rect, 2, border_radius=8)
                    equip_surf = self.font.render("EQUIP", True, button_text_color)
                    equip_rect = equip_surf.get_rect(center=btn_rect.center)
                    grid_surface.blit(equip_surf, equip_rect)
            else:
                button_fill_color = self.neon_green if is_button_hovered else self.gray
                button_text_color = self.bg_color if is_button_hovered else self.neon_green
                pygame.draw.rect(grid_surface, button_fill_color, btn_rect, 0, border_radius=8)
                pygame.draw.rect(grid_surface, self.neon_green, btn_rect, 2, border_radius=8)
                buy_text = f"BUY {item.cost} Mb"
                buy_surf = self.font.render(buy_text, True, button_text_color)
                buy_rect = buy_surf.get_rect(center=btn_rect.center)
                grid_surface.blit(buy_surf, buy_rect)

        self.screen.blit(grid_surface, (grid_viewport_rect.x, grid_viewport_rect.y))

        # Draw scrollbar
        if max_scroll > 0:
            bar_w = 12
            bar_h = int(grid_viewport_rect.height * (visible_viewport_height / content_height))
            bar_h = max(30, bar_h) 
            bar_y = int(grid_viewport_rect.y + (self.scroll_offset / max_scroll) * (grid_viewport_rect.height - bar_h))
            bar_rect = pygame.Rect(grid_viewport_rect.right + 8, bar_y, bar_w, bar_h)
            pygame.draw.rect(self.screen, self.neon_green, bar_rect, border_radius=4)

        # Currency display (Mb)
        mb_x = self.width - 180
        mb_y = self.height - 50
        mb_text = self.font.render(f"DATA: {coins} Mb", True, self.neon_blue)
        self.screen.blit(mb_text, (mb_x, mb_y))


        # Popup for not enough data
        if self.show_not_enough_data:
            popup_w, popup_h = 400, 150
            popup_x = (self.width - popup_w) // 2
            popup_y = (self.height - popup_h) // 2
            popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
            pygame.draw.rect(self.screen, self.dark_gray, popup_rect, border_radius=16)
            pygame.draw.rect(self.screen, self.error_color, popup_rect, 4, border_radius=16)
            
            msg = self.large_font.render("ACCESS DENIED!", True, self.error_color)
            msg_rect = msg.get_rect(center=(popup_rect.centerx, popup_y + 40))
            self.screen.blit(msg, msg_rect)

            sub_msg = self.font.render("INSUFFICIENT DATA", True, self.neon_green)
            sub_msg_rect = sub_msg.get_rect(center=(popup_rect.centerx, popup_y + 75))
            self.screen.blit(sub_msg, sub_msg_rect)

            ok_rect = pygame.Rect(popup_x + (popup_w - 100) // 2, popup_y + 110, 100, 30)
            ok_is_hovered = ok_rect.collidepoint(mouse_pos)
            ok_fill_color = self.neon_green if ok_is_hovered else self.gray
            ok_text_color = self.bg_color if ok_is_hovered else self.neon_green

            pygame.draw.rect(self.screen, ok_fill_color, ok_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.neon_green, ok_rect, 2, border_radius=8)
            ok_text = self.font.render("OVERRIDE", True, ok_text_color)
            ok_text_rect = ok_text.get_rect(center=ok_rect.center)
            self.screen.blit(ok_text, ok_text_rect)
            self.not_enough_data_ok_rect = ok_rect
        else:
            self.not_enough_data_ok_rect = None

        pygame.display.flip()

    def handle_event(self, event):
        category = self.current_sub_tab[self.current_tab]
        all_items = self.get_items(category)
        owned_key = "owned_" + category.lower() + "s"
        owned_list = getattr(self.data_manager, f"get_{owned_key}")()

        if self.current_tab == "Shop":
            display_items = [item for item in all_items if item.name not in owned_list]
        else:
            display_items = [item for item in all_items if item.name in owned_list]
        
        cols = self.grid_cols
        visible_rows = self.visible_rows
        total_rows = (len(display_items) + cols - 1) // cols
        cell_height = self.cell_height + self.cell_margin
        content_height = total_rows * cell_height
        visible_viewport_height = visible_rows * cell_height - self.cell_margin
        max_scroll = max(0, content_height - visible_viewport_height)


        # Handle popup OK button
        if self.show_not_enough_data:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.not_enough_data_ok_rect and self.not_enough_data_ok_rect.collidepoint(event.pos):
                    self.show_not_enough_data = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.back_button.collidepoint(mouse_pos):
                return "back"

            for rect, tab_name in self.tab_rects:
                if rect.collidepoint(mouse_pos):
                    if self.current_tab != tab_name:
                        self.current_tab = tab_name
                        self.target_scroll_offset = 0
                    return

            for rect, sub_tab_name in self.sub_tab_rects:
                if rect.collidepoint(mouse_pos):
                    if self.current_sub_tab[self.current_tab] != sub_tab_name:
                        self.current_sub_tab[self.current_tab] = sub_tab_name
                        self.target_scroll_offset = 0
                    return

            if self.scroll_up_btn.collidepoint(mouse_pos):
                self.target_scroll_offset = max(0, self.target_scroll_offset - self.scroll_speed)
                return

            if self.scroll_down_btn.collidepoint(mouse_pos):
                self.target_scroll_offset = min(max_scroll, self.target_scroll_offset + self.scroll_speed)
                return

            # Handle grid button clicks
            if self.hovered_button:
                i, item = self.hovered_button
                equipped_key = "equipped_" + category.lower()
                equipped_id = getattr(self.data_manager, f"get_{equipped_key}")()

                if item.name in owned_list:
                    if equipped_id != item.name:
                        if category == "Skin":
                            self.data_manager.set_equipped_skin(item.name)
                        elif category == "Trail":
                            self.data_manager.set_equipped_trail(item.name)
                else:
                    if self.data_manager.get_coins() >= item.cost:
                        self.data_manager.spend_coins(item.cost)
                        if category == "Skin":
                            self.data_manager.unlock_skin(item.name)
                            self.data_manager.set_equipped_skin(item.name)
                        elif category == "Trail":
                            self.data_manager.unlock_trail(item.name)
                            self.data_manager.set_equipped_trail(item.name)
                    else:
                        self.show_not_enough_data = True
                return

        elif event.type == pygame.MOUSEWHEEL:
            self.target_scroll_offset -= event.y * self.scroll_speed
            self.target_scroll_offset = max(0, min(self.target_scroll_offset, max_scroll))
            return

    def get_selected_skin(self):
        return self.data_manager.get_equipped_skin()

    def get_selected_trail(self):
        return self.data_manager.get_equipped_trail()
    
