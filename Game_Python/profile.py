"""
Profile management screen for SI3LN Game
Allows user to modify character, username, and password
Shows locked/unlocked character status
"""
import pygame
from constants import *
from ui_components import Button, InputField, Panel, ImageButton


class ProfileScreen:
    def __init__(self, screen, auth_system, players):
        self.screen = screen
        self.auth = auth_system
        self.players = players
        self.active = False
        
        # Get screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Lock icon (simple drawn lock)
        self.lock_icon = self._create_lock_icon()
        
        self.setup_ui()
    
    def _create_lock_icon(self):
        """Create a small lock icon surface"""
        size = 24
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Lock body
        pygame.draw.rect(surf, (200, 200, 200), (4, 10, 16, 14), border_radius=2)
        # Lock shackle
        pygame.draw.arc(surf, (200, 200, 200), (6, 2, 12, 12), 3.14, 0, 2)
        return surf
    
    def _is_character_unlocked(self, char_idx):
        """Check if a character is unlocked for the current user"""
        if char_idx < 7:
            # Characters 0-6 are always unlocked
            return True
        
        if char_idx == 7:
            # Phantom Striker requires unlock
            if self.auth.guest_mode:
                return False
            user_data = self.auth.get_user_data()
            if not user_data:
                return False
            unlocked = user_data.get("unlocked_characters", [0])
            return char_idx in unlocked
        
        return False
    
    def setup_ui(self):
        """Setup UI components"""
        # Get small font for this screen
        self.font_title = pygame.font.Font(None, 50)
        self.font_medium = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        
        # Panel
        panel_width = 700
        panel_height = 600
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        self.panel = Panel(panel_x, panel_y, panel_width, panel_height)
        
        # Character selection buttons (all characters, including locked ones)
        self.character_buttons = []
        start_x = panel_x + 50
        start_y = panel_y + 150
        for i in range(min(len(CHARACTER_NAMES), len(self.players))):
            row = i // 4
            col = i % 4
            x = start_x + col * 120
            y = start_y + row * 120
            btn = ImageButton(x + 50, y + 50, 80, 80, self.players[i], 
                            self.font_small, CHARACTER_NAMES[i])
            self.character_buttons.append(btn)
        
        # Input fields
        input_x = panel_x + 50
        input_y = panel_y + 380
        input_width = 300
        
        self.username_input = InputField(input_x, input_y, input_width, 40, 
                                        self.font_small, "Nouveau pseudo:")
        self.old_password_input = InputField(input_x + 350, input_y, input_width, 40,
                                            self.font_small, "Ancien MDP:", 
                                            password=True)
        self.new_password_input = InputField(input_x, input_y + 80, input_width, 40,
                                            self.font_small, "Nouveau MDP:", 
                                            password=True)
        self.confirm_password_input = InputField(input_x + 350, input_y + 80, input_width, 40,
                                                self.font_small, "Confirmer:", 
                                                password=True)
        
        # Buttons
        self.save_button = Button(panel_x + panel_width // 2 - 120, 
                                  panel_y + panel_height - 50,
                                  200, 50, "SAUVEGARDER", self.font_medium,
                                  bg_color=GREEN)
        self.close_button = Button(panel_x + panel_width // 2 + 120,
                                   panel_y + panel_height - 50,
                                   150, 50, "FERMER", self.font_medium,
                                   bg_color=RED)
        
        # Message
        self.message = ""
        self.message_color = WHITE
        self.message_timer = 0
        
        # Selected character
        self.selected_character = 0
    
    def open(self):
        """Open profile screen"""
        self.active = True
        
        # Load current user data
        if not self.auth.guest_mode and self.auth.current_user:
            user_data = self.auth.get_user_data()
            self.selected_character = user_data.get("selected_character", 0)
            self.username_input.text = ""  # Don't pre-fill to avoid accidental changes
        elif self.auth.guest_mode:
            self.selected_character = self.auth.guest_character
        
        # Update character selection (only select if unlocked)
        for i, btn in enumerate(self.character_buttons):
            btn.selected = (i == self.selected_character)
        
        # Clear inputs
        self.old_password_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()
        self.message = ""
    
    def close(self):
        """Close profile screen"""
        self.active = False
    
    def handle_event(self, event):
        """Handle events for profile screen"""
        if not self.active:
            return False
        
        # Handle input fields
        self.username_input.handle_event(event)
        self.old_password_input.handle_event(event)
        self.new_password_input.handle_event(event)
        self.confirm_password_input.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Character selection
            for i, btn in enumerate(self.character_buttons):
                if btn.is_clicked(pos):
                    if self._is_character_unlocked(i):
                        self.selected_character = i
                        for j, b in enumerate(self.character_buttons):
                            b.selected = (j == i)
                    else:
                        # Show locked message
                        self.message = f"{CHARACTER_NAMES[i]} est verrouillé!"
                        self.message_color = RED
                        self.message_timer = 180
            
            # Save button
            if self.save_button.is_clicked(pos):
                self.save_changes()
            
            # Close button
            if self.close_button.is_clicked(pos):
                self.close()
                return True
        
        return False
    
    def save_changes(self):
        """Save profile changes"""
        if self.auth.guest_mode:
            self.message = "Mode invité - modifications non sauvegardées"
            self.message_color = ORANGE
            self.message_timer = 180
            # Still update guest character
            self.auth.guest_character = self.selected_character
            return
        
        changes_made = False
        
        # Update character
        if self.selected_character != self.auth.get_user_data("selected_character"):
            self.auth.update_user_data(selected_character=self.selected_character)
            changes_made = True
        
        # Change username
        new_username = self.username_input.get_text().strip()
        if new_username and new_username != self.auth.current_user:
            success, msg = self.auth.change_username(new_username)
            if success:
                changes_made = True
                self.message = msg
                self.message_color = GREEN
            else:
                self.message = msg
                self.message_color = RED
                self.message_timer = 180
                return
        
        # Change password
        old_pass = self.old_password_input.get_text()
        new_pass = self.new_password_input.get_text()
        confirm_pass = self.confirm_password_input.get_text()
        
        if old_pass or new_pass or confirm_pass:
            if not old_pass:
                self.message = "Entrez l'ancien mot de passe"
                self.message_color = RED
                self.message_timer = 180
                return
            
            if new_pass != confirm_pass:
                self.message = "Les mots de passe ne correspondent pas"
                self.message_color = RED
                self.message_timer = 180
                return
            
            success, msg = self.auth.change_password(old_pass, new_pass)
            if success:
                changes_made = True
                self.message = msg
                self.message_color = GREEN
            else:
                self.message = msg
                self.message_color = RED
                self.message_timer = 180
                return
        
        if changes_made:
            self.message = "Profil mis à jour avec succès!"
            self.message_color = GREEN
            self.message_timer = 180
            # Clear password fields
            self.old_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()
        else:
            self.message = "Aucune modification détectée"
            self.message_color = ORANGE
            self.message_timer = 180
    
    def update(self):
        """Update profile screen"""
        if not self.active:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update buttons
        for btn in self.character_buttons:
            btn.update(mouse_pos)
        self.save_button.update(mouse_pos)
        self.close_button.update(mouse_pos)
        
        # Update input fields
        self.username_input.update()
        self.old_password_input.update()
        self.new_password_input.update()
        self.confirm_password_input.update()
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""
    
    def draw(self):
        """Draw profile screen"""
        if not self.active:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Draw panel
        self.panel.draw(self.screen)
        
        # Draw title
        title = self.font_title.render("PROFIL", True, WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, 
                                            self.panel.rect.y + 40))
        self.screen.blit(title, title_rect)
        
        # Draw username display
        username = self.auth.current_user if self.auth.current_user else "Invité"
        user_text = self.font_medium.render(f"Joueur: {username}", True, CYAN)
        self.screen.blit(user_text, (self.panel.rect.x + 50, self.panel.rect.y + 90))
        
        # Draw character selection label
        char_label = self.font_medium.render("Choisir personnage:", True, WHITE)
        self.screen.blit(char_label, (self.panel.rect.x + 50, self.panel.rect.y + 120))
        
        # Draw character buttons with lock overlay for locked characters
        for i, btn in enumerate(self.character_buttons):
            btn.draw(self.screen)
            
            # Draw lock icon if character is locked
            if not self._is_character_unlocked(i):
                # Darken the button area
                darken = pygame.Surface((btn.rect.width, btn.rect.height), pygame.SRCALPHA)
                darken.fill((0, 0, 0, 160))
                self.screen.blit(darken, btn.rect.topleft)
                
                # Draw lock icon in center
                lock_rect = self.lock_icon.get_rect(center=btn.rect.center)
                self.screen.blit(self.lock_icon, lock_rect)
                
                # Draw "LOCKED" text below
                locked_text = self.font_small.render("VERROUILLE", True, LIGHT_GRAY)
                locked_rect = locked_text.get_rect(center=(btn.rect.centerx, btn.rect.bottom + 10))
                self.screen.blit(locked_text, locked_rect)
        
        # Draw unlock hint for Phantom Striker
        if not self._is_character_unlocked(7):
            hint_text = self.font_small.render(
                "Debloquer: Niveau 3 + 5000 pts", True, ORANGE
            )
            hint_rect = hint_text.get_rect(
                center=(self.character_buttons[7].rect.centerx, 
                        self.character_buttons[7].rect.bottom + 28)
            )
            self.screen.blit(hint_text, hint_rect)
        
        # Draw input fields (only if not guest)
        if not self.auth.guest_mode:
            self.username_input.draw(self.screen)
            self.old_password_input.draw(self.screen)
            self.new_password_input.draw(self.screen)
            self.confirm_password_input.draw(self.screen)
        else:
            guest_msg = self.font_small.render(
                "Mode invité - Créez un compte pour sauvegarder vos modifications",
                True, ORANGE
            )
            self.screen.blit(guest_msg, (self.panel.rect.x + 50, 
                                         self.panel.rect.y + 400))
        
        # Draw buttons
        self.save_button.draw(self.screen)
        self.close_button.draw(self.screen)
        
        # Draw message
        if self.message:
            msg_surf = self.font_small.render(self.message, True, self.message_color)
            msg_rect = msg_surf.get_rect(center=(self.screen_width // 2,
                                                 self.panel.rect.bottom - 100))
            self.screen.blit(msg_surf, msg_rect)
    
    def get_selected_character(self):
        """Get currently selected character"""
        return self.selected_character
