"""
Level selection screen for SI3LN Game
Allows selection of worlds and levels within worlds
"""
import pygame
from constants import *
from ui_components import Button, Panel
from utils import load_image


class LevelSelector:
    def __init__(self, screen, worlds_config):
        self.screen = screen
        self.worlds = worlds_config
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        self.selected_world = "Space"  # Default world
        self.selected_level = 1
        self.active = False
        self.view = "WORLDS"  # "WORLDS" or "LEVELS"
        
        # World unlock state: worlds unlock sequentially — finishing all levels
        # of a world unlocks the next one. Boot Camp is playable by default.
        # Progress is restored from the saved profile in open() (see _restore_from_auth).
        self.boot_camp_completed = False
        self.world_order = list(self.worlds.keys())
        self.world_unlocked = {world: False for world in self.worlds}
        if "BootCamp" in self.world_unlocked:
            self.world_unlocked["BootCamp"] = True
        # Set by game.py so open() can restore/persist progress across sessions.
        self.auth = None
        
        # Load world backgrounds
        self.world_backgrounds = {}
        for world_key, world_data in self.worlds.items():
            try:
                # Load the background for each world
                bg_path = f"worlds/{world_data['background']}"
                bg_img = load_image(bg_path, (300, 200))
                self.world_backgrounds[world_key] = bg_img
            except Exception as e:
                print(f"Error loading background for {world_key}: {e}")
                self.world_backgrounds[world_key] = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        # Load Arcade Classic font
        try:
            arcade_font_path = "assets/fonts/ArcadeClassic/ArcadeClassic.TTF"
            self.font_title = pygame.font.Font(arcade_font_path, 60)
            self.font_medium = pygame.font.Font(arcade_font_path, 35)
            self.font_small = pygame.font.Font(arcade_font_path, 28)
        except:
            self.font_title = pygame.font.Font(None, 60)
            self.font_medium = pygame.font.Font(None, 35)
            self.font_small = pygame.font.Font(None, 28)
        
        # Create world cards
        self.world_cards = []
        card_width = 300
        card_height = 200
        spacing = 40
        
        worlds_list = list(self.worlds.keys())
        
        # Layout: 3 cards on top row (centered), 3 cards on bottom row (centered)
        # Top row: BootCamp + first 2 worlds
        top_row_cards = worlds_list[:3]
        total_width_top = 3 * card_width + 2 * spacing
        start_x_top = (self.screen_width - total_width_top) // 2
        start_y = 150
        
        for i, world_key in enumerate(top_row_cards):
            x = start_x_top + i * (card_width + spacing)
            y = start_y
            
            card = WorldCard(x, y, card_width, card_height,
                           world_key, self.worlds[world_key],
                           self.world_backgrounds[world_key])
            self.world_cards.append(card)
        
        # Bottom row: remaining worlds
        if len(worlds_list) > 3:
            bottom_row_cards = worlds_list[3:]
            total_width_bottom = len(bottom_row_cards) * card_width + (len(bottom_row_cards) - 1) * spacing
            start_x_bottom = (self.screen_width - total_width_bottom) // 2
            
            for i, world_key in enumerate(bottom_row_cards):
                x = start_x_bottom + i * (card_width + spacing)
                y = start_y + card_height + spacing
                
                card = WorldCard(x, y, card_width, card_height,
                               world_key, self.worlds[world_key],
                               self.world_backgrounds[world_key])
                self.world_cards.append(card)
        
        # Level buttons (will be created dynamically based on selected world)
        self.level_buttons = []
        
        # Back button
        self.back_button = Button(100, self.screen_height - 80,
                                  150, 60, "RETOUR",
                                  self.font_small, bg_color=None, 
                                  text_color=WHITE, border_color=WHITE)
        
        self.create_level_buttons()
    
    def create_level_buttons(self):
        """Create level buttons for selected world as a vertical list"""
        self.level_buttons = []
        
        if self.selected_world not in self.worlds:
            return
        
        num_levels = self.worlds[self.selected_world]["levels"]
        
        # Create vertical list of level buttons
        button_width = 600
        button_height = 60
        spacing = 15
        
        start_x = (self.screen_width - button_width) // 2
        start_y = 180
        
        for i in range(num_levels):
            x = start_x + button_width // 2
            y = start_y + i * (button_height + spacing) + button_height // 2
            
            level_text = f"Niveau {i + 1}"
            
            btn = Button(x, y, button_width, button_height,
                        level_text,
                        self.font_medium,
                        bg_color=None, text_color=WHITE, border_color=WHITE)
            self.level_buttons.append(btn)
        
        # Start button - always at bottom of screen
        self.start_button = Button(self.screen_width // 2, 
                                   self.screen_height - 100,
                                   300, 70, "COMMENCER", 
                                   self.font_medium,
                                   bg_color=None, text_color=GREEN, border_color=GREEN, border_width=4)
    
    def open(self):
        """Open level selector"""
        self.active = True
        self.view = "WORLDS"  # Start with world selection
        # Restore unlock progress from the saved profile every time we open,
        # so it survives across sessions (was previously lost on every launch).
        self._restore_from_auth()
        # Update selected state for cards
        for card in self.world_cards:
            card.selected = (card.world_name == self.selected_world)

    def _restore_from_auth(self):
        """Rebuild world_unlocked from the persisted profile (if logged in)."""
        if not self.auth:
            return
        data = self.auth.get_user_data()
        if not data:
            return
        for world_name in data.get("unlocked_worlds", []):
            if world_name in self.world_unlocked:
                self.world_unlocked[world_name] = True
        # Backward-compat with older saves that only stored a boot-camp flag.
        if data.get("boot_camp_completed"):
            self.boot_camp_completed = True
            self._unlock_next("BootCamp", persist=False)

    def _unlock_next(self, completed_world, persist=True):
        """Unlock the world that follows *completed_world* in world_order."""
        if completed_world in self.world_order:
            self.world_unlocked[completed_world] = True
            idx = self.world_order.index(completed_world)
            if idx + 1 < len(self.world_order):
                self.world_unlocked[self.world_order[idx + 1]] = True
        if persist and self.auth and not self.auth.guest_mode and self.auth.current_user:
            unlocked_now = [w for w, ok in self.world_unlocked.items() if ok]
            self.auth.update_user_data(
                unlocked_worlds=unlocked_now,
                boot_camp_completed=self.boot_camp_completed,
            )

    def unlock_next_world(self, completed_world, auth=None):
        """Called when a world's levels are all cleared — unlocks the next world."""
        if auth is not None:
            self.auth = auth
        if completed_world == "BootCamp":
            self.boot_camp_completed = True
        self._unlock_next(completed_world, persist=True)
    
    def set_world_unlocked(self, world_name, unlocked=True):
        """Set world unlock status"""
        if world_name in self.world_unlocked:
            self.world_unlocked[world_name] = unlocked
    
    def set_boot_camp_completed(self, completed=True, auth=None):
        """Mark Boot Camp as completed — unlocks the next world (Space)."""
        if auth is not None:
            self.auth = auth
        self.boot_camp_completed = completed
        if completed:
            self.unlock_next_world("BootCamp", auth)
    
    def close(self):
        """Close level selector"""
        self.active = False
    
    def handle_event(self, event):
        """Handle events"""
        if not self.active:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            if self.view == "WORLDS":
                # World card selection
                for card in self.world_cards:
                    if card.is_clicked(pos):
                        # Check if world is unlocked
                        if not self.world_unlocked.get(card.world_name, False):
                            print(f"[DEBUG] World {card.world_name} is locked!")
                            return ("WORLD_LOCKED", card.world_name)
                        
                        self.selected_world = card.world_name
                        self.selected_level = 1
                        self.create_level_buttons()
                        self.view = "LEVELS"  # Switch to level selection
                        # Update selected state
                        for c in self.world_cards:
                            c.selected = (c.world_name == self.selected_world)
                        return None
                
                # Back button in world view
                if self.back_button.is_clicked(pos):
                    return ("BACK",)
            
            elif self.view == "LEVELS":
                # Level selection
                for i, btn in enumerate(self.level_buttons):
                    if btn.is_clicked(pos):
                        self.selected_level = i + 1
                        print(f"[DEBUG] Level {self.selected_level} selected")
                
                # Start button
                print(f"[DEBUG] Checking start button click at pos {pos}")
                print(f"[DEBUG] Start button rect: {self.start_button.rect}")
                print(f"[DEBUG] Start button enabled: {self.start_button.enabled}")
                if self.start_button.is_clicked(pos):
                    print(f"[DEBUG] Start button clicked! World={self.selected_world}, Level={self.selected_level}")
                    return ("START_LEVEL", self.selected_world, self.selected_level)
                else:
                    print(f"[DEBUG] Start button NOT clicked")
                
                # Back button in level view
                if self.back_button.is_clicked(pos):
                    self.view = "WORLDS"  # Go back to world selection
                    return None
        
        return None
    
    def update(self, mouse_pos=None):
        """Update level selector.

        Args:
            mouse_pos: Pre-transformed mouse position in reference
                       (canvas) space supplied by the caller.  When
                       omitted the raw screen position from
                       pygame.mouse.get_pos() is used directly (legacy
                       behaviour, correct only when not using a
                       ResolutionManager canvas).
        """
        if not self.active:
            return

        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        
        if self.view == "WORLDS":
            # Update world cards
            for card in self.world_cards:
                card.update(mouse_pos)
        
        elif self.view == "LEVELS":
            # Update level buttons
            for btn in self.level_buttons:
                btn.update(mouse_pos)
            
            self.start_button.update(mouse_pos)
        
        self.back_button.update(mouse_pos)
    
    def draw(self, background=None):
        """Draw level selector"""
        if not self.active:
            return
        
        # Draw background
        if background:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((10, 10, 30))
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        if self.view == "WORLDS":
            # Draw title
            title = self.font_title.render("CHOISISSEZ VOTRE MONDE", True, CYAN)
            title_rect = title.get_rect(center=(self.screen_width // 2, 60))
            self.screen.blit(title, title_rect)
            
            # Draw world cards
            for card in self.world_cards:
                card.draw(self.screen)
                # Draw lock overlay for locked worlds
                if not self.world_unlocked.get(card.world_name, False):
                    lock_overlay = pygame.Surface((card.rect.width, card.rect.height), pygame.SRCALPHA)
                    lock_overlay.fill((0, 0, 0, 150))
                    self.screen.blit(lock_overlay, card.rect)
                    # Draw lock icon
                    lock_font = pygame.font.Font(None, 60)
                    lock_text = lock_font.render("🔒", True, GRAY)
                    lock_rect = lock_text.get_rect(center=card.rect.center)
                    self.screen.blit(lock_text, lock_rect)
                    # Draw lock text
                    lock_label = self.font_small.render("VERROUILLÉ", True, GRAY)
                    lock_label_rect = lock_label.get_rect(center=(card.rect.centerx, card.rect.centery + 40))
                    self.screen.blit(lock_label, lock_label_rect)
            
            # Draw instruction
            instruction = pygame.font.Font(None, 24).render("Cliquez sur un monde pour continuer", True, WHITE)
            inst_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 120))
            self.screen.blit(instruction, inst_rect)
            
            # Boot camp hint
            if not self.boot_camp_completed:
                hint = self.font_small.render("Complétez le Boot Camp pour débloquer les autres mondes", True, HOLO_BLUE)
                hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 150))
                self.screen.blit(hint, hint_rect)
        
        elif self.view == "LEVELS":
            # Draw title
            world_name = self.worlds[self.selected_world]["name"]
            title = self.font_title.render(world_name, True, CYAN)
            title_rect = title.get_rect(center=(self.screen_width // 2, 60))
            self.screen.blit(title, title_rect)
            
            # Draw level label
            level_label = self.font_medium.render("CHOISISSEZ UN NIVEAU", True, WHITE)
            level_label_rect = level_label.get_rect(center=(self.screen_width // 2, 140))
            self.screen.blit(level_label, level_label_rect)
            
            # Draw level buttons (list format)
            for i, btn in enumerate(self.level_buttons):
                # Highlight selected level
                if i + 1 == self.selected_level:
                    btn.bg_color = (80, 80, 150)
                    btn.border_color = YELLOW
                    btn.border_width = 5
                    btn.text_color = YELLOW
                else:
                    btn.bg_color = None
                    btn.border_color = WHITE
                    btn.border_width = 3
                    btn.text_color = WHITE
                btn.draw(self.screen)
            
            # Draw start button
            self.start_button.draw(self.screen)
        
        # Draw back button
        self.back_button.draw(self.screen)
    
    def get_selected_level_info(self):
        """Get info about selected level"""
        return {
            "world": self.selected_world,
            "level": self.selected_level,
            "world_data": self.worlds[self.selected_world]
        }


class WorldCard:
    """Represents a world selection card with background image"""
    def __init__(self, x, y, width, height, world_name, world_data, bg_image):
        self.rect = pygame.Rect(x, y, width, height)
        self.world_name = world_name
        self.world_data = world_data
        self.bg_image = bg_image
        self.hovered = False
        self.selected = False
        
        # Scale background image to card size
        if self.bg_image:
            self.bg_image = pygame.transform.scale(self.bg_image, (width, height))
        
        # Font for world name
        self.font = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 24)
    
    def draw(self, screen):
        """Draw the world card"""
        # Draw background image
        if self.bg_image:
            screen.blit(self.bg_image, self.rect)
        else:
            pygame.draw.rect(screen, (30, 30, 60), self.rect)
        
        # Draw overlay for visibility
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if self.selected:
            overlay.fill((0, 200, 255, 80))  # Cyan semi-transparent
        elif self.hovered:
            overlay.fill((255, 255, 255, 40))  # White semi-transparent
        else:
            overlay.fill((0, 0, 0, 60))  # Dark but still show image
        screen.blit(overlay, self.rect)
        
        # Draw border
        border_color = CYAN if self.selected else (YELLOW if self.hovered else WHITE)
        border_width = 5 if self.selected else 3
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=10)
        
        # Draw world name
        name_surf = self.font.render(self.world_data["name"], True, WHITE)
        name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.centery))
        
        # Shadow for text
        shadow_surf = self.font.render(self.world_data["name"], True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        screen.blit(shadow_surf, shadow_rect)
        screen.blit(name_surf, name_rect)
        
        # Draw level count
        level_text = f"{self.world_data['levels']} niveaux"
        level_surf = self.font_small.render(level_text, True, WHITE)
        level_rect = level_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 30))
        shadow_level = self.font_small.render(level_text, True, BLACK)
        shadow_level_rect = shadow_level.get_rect(center=(self.rect.centerx + 1, self.rect.bottom - 29))
        screen.blit(shadow_level, shadow_level_rect)
        screen.blit(level_surf, level_rect)
    
    def update(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, pos):
        """Check if card is clicked"""
        return self.rect.collidepoint(pos)
