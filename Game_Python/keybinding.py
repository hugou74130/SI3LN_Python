"""
Keybinding / input mapping system for SI3LN Game.
Loads and saves user-defined controls from data/keybinds.json.
"""
import json
import os
import pygame


# Default keyboard controls. Each action maps to a list of pygame key codes.
DEFAULT_KEYBINDS = {
    "move_left": [pygame.K_LEFT, pygame.K_a],
    "move_right": [pygame.K_RIGHT, pygame.K_d],
    "move_up": [pygame.K_UP, pygame.K_w],
    "move_down": [pygame.K_DOWN, pygame.K_s],
    "shoot": [pygame.K_SPACE],
    "shield": [pygame.K_b],
    "mega_shot": [pygame.K_LSHIFT, pygame.K_RSHIFT],
    "special_attack": [pygame.K_x],
    "phase_dash": [pygame.K_LCTRL, pygame.K_RCTRL],
    "fullscreen": [pygame.K_F11],
    "menu_back": [pygame.K_ESCAPE],
}


# Human-readable French labels for the settings screen
ACTION_LABELS = {
    "move_left": "Gauche",
    "move_right": "Droite",
    "move_up": "Haut",
    "move_down": "Bas",
    "shoot": "Tirer",
    "shield": "Bouclier",
    "mega_shot": "Mega tir",
    "special_attack": "Attaque speciale",
    "phase_dash": "Phase Dash",
    "fullscreen": "Plein ecran",
    "menu_back": "Retour menu",
}


class KeybindingManager:
    """Loads, saves and resolves key bindings."""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.keybinds_file = os.path.join(data_dir, "keybinds.json")
        self.keybinds = self.load()

    def load(self):
        """Load keybinds from JSON, falling back to defaults."""
        if os.path.exists(self.keybinds_file):
            try:
                with open(self.keybinds_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                # Convert stored integer codes back to lists
                keybinds = {}
                for action, codes in raw.items():
                    if isinstance(codes, int):
                        codes = [codes]
                    elif not isinstance(codes, list):
                        codes = []
                    keybinds[action] = [int(c) for c in codes]
                # Ensure all default actions exist
                for action, codes in DEFAULT_KEYBINDS.items():
                    if action not in keybinds:
                        keybinds[action] = list(codes)
                return keybinds
            except Exception as e:
                print(f"Error loading keybinds: {e}")
        return {k: list(v) for k, v in DEFAULT_KEYBINDS.items()}

    def save(self):
        """Save current keybinds to JSON."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.keybinds_file, "w", encoding="utf-8") as f:
                json.dump(self.keybinds, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving keybinds: {e}")

    def reset_to_defaults(self):
        """Reset all bindings to default values."""
        self.keybinds = {k: list(v) for k, v in DEFAULT_KEYBINDS.items()}
        self.save()

    def get_codes(self, action):
        """Return list of pygame key codes bound to an action."""
        return self.keybinds.get(action, [])

    def is_pressed(self, keys, action):
        """Check if any key bound to action is currently pressed."""
        return any(keys[code] for code in self.get_codes(action) if 0 <= code < len(keys))

    def is_action_key(self, event_key, action):
        """Check if a KEYDOWN/KEYUP event key matches an action."""
        return event_key in self.get_codes(action)

    def set_binding(self, action, codes):
        """Set key codes for an action and persist."""
        if isinstance(codes, int):
            codes = [codes]
        self.keybinds[action] = list(codes)
        self.save()

    def add_binding(self, action, code):
        """Add an additional key code to an action."""
        codes = self.keybinds.setdefault(action, [])
        if code not in codes:
            codes.append(code)
        self.save()

    def remove_binding(self, action, code):
        """Remove a key code from an action."""
        codes = self.keybinds.get(action, [])
        if code in codes:
            codes.remove(code)
        self.save()

    @staticmethod
    def key_name(code):
        """Return a human-readable name for a pygame key code."""
        name = pygame.key.name(code)
        # Provide nicer labels for common keys
        mapping = {
            "left": "←",
            "right": "→",
            "up": "↑",
            "down": "↓",
            "space": "ESPACE",
            "left shift": "SHIFT",
            "right shift": "SHIFT",
            "left ctrl": "CTRL",
            "right ctrl": "CTRL",
            "left alt": "ALT",
            "right alt": "ALT",
            "return": "ENTREE",
            "escape": "ECHAP",
        }
        return mapping.get(name.lower(), name.upper())

    def format_binding(self, action):
        """Return a human-readable string for an action's bindings."""
        codes = self.get_codes(action)
        if not codes:
            return "Non assigne"
        return " / ".join(self.key_name(c) for c in codes)


class KeybindingScreen:
    """Simple keybinding settings screen."""

    def __init__(self, game, keybinding_manager):
        self.game = game
        self.keybinding = keybinding_manager
        self.active = False
        self.selected_action = None
        self.waiting_for_key = False
        self.actions = list(DEFAULT_KEYBINDS.keys())
        self.font = game.font_small
        self.font_title = game.font_large
        self.font_tiny = game.font_tiny
        self.buttons = []
        self.back_button = None
        self.reset_button = None
        self._build_buttons()

    def _build_buttons(self):
        """Rebuild button rectangles for current screen size."""
        sw = self.game.screen_width
        sh = self.game.screen_height
        self.buttons = []
        start_y = 140
        row_h = 42
        label_w = 250
        value_w = 220
        x_label = sw // 2 - label_w - 20
        x_value = sw // 2 + 20
        for i, action in enumerate(self.actions):
            y = start_y + i * row_h
            label_rect = pygame.Rect(x_label, y, label_w, 34)
            value_rect = pygame.Rect(x_value, y, value_w, 34)
            self.buttons.append({
                "action": action,
                "label_rect": label_rect,
                "value_rect": value_rect,
            })
        self.back_button = pygame.Rect(sw // 2 - 220, sh - 80, 200, 45)
        self.reset_button = pygame.Rect(sw // 2 + 20, sh - 80, 200, 45)

    def open(self):
        self.active = True
        self.selected_action = None
        self.waiting_for_key = False
        self._build_buttons()

    def close(self):
        self.active = False
        self.selected_action = None
        self.waiting_for_key = False

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if self.waiting_for_key and self.selected_action:
                # Ignore modifier-only keys for primary binding
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT,
                                 pygame.K_LCTRL, pygame.K_RCTRL,
                                 pygame.K_LALT, pygame.K_RALT):
                    return
                self.keybinding.set_binding(self.selected_action, [event.key])
                self.waiting_for_key = False
                self.selected_action = None
                return
            if self.keybinding.is_action_key(event.key, "menu_back"):
                self.close()
                return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = self.game.rm.screen_to_ref(*event.pos)
            if self.back_button.collidepoint(pos):
                self.close()
                return
            if self.reset_button.collidepoint(pos):
                self.keybinding.reset_to_defaults()
                return
            for btn in self.buttons:
                if btn["value_rect"].collidepoint(pos):
                    self.selected_action = btn["action"]
                    self.waiting_for_key = True
                    return

    def draw(self, screen):
        if not self.active:
            return
        # Dark background
        overlay = pygame.Surface((self.game.screen_width, self.game.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Title
        title = self.font_title.render("CONTROLES", True, WHITE)
        title_rect = title.get_rect(center=(self.game.screen_width // 2, 70))
        screen.blit(title, title_rect)

        # Instructions
        if self.waiting_for_key:
            hint = self.font.render(f"Appuie sur une touche pour: {ACTION_LABELS.get(self.selected_action, self.selected_action)}", True, YELLOW)
        else:
            hint = self.font.render("Clique sur une touche pour la modifier", True, LIGHT_GRAY)
        hint_rect = hint.get_rect(center=(self.game.screen_width // 2, 110))
        screen.blit(hint, hint_rect)

        # Action rows
        for btn in self.buttons:
            action = btn["action"]
            label_color = CYAN if self.selected_action == action else WHITE
            label = self.font.render(ACTION_LABELS.get(action, action), True, label_color)
            screen.blit(label, (btn["label_rect"].x + 10, btn["label_rect"].centery - label.get_height() // 2))

            value_color = YELLOW if self.selected_action == action else WHITE
            value_text = self.keybinding.format_binding(action)
            value = self.font.render(value_text, True, value_color)
            # Draw value box
            pygame.draw.rect(screen, DARK_GRAY, btn["value_rect"], border_radius=5)
            pygame.draw.rect(screen, WHITE if self.selected_action != action else YELLOW, btn["value_rect"], 2, border_radius=5)
            screen.blit(value, (btn["value_rect"].x + 10, btn["value_rect"].centery - value.get_height() // 2))

        # Back and Reset buttons
        mouse_pos = self.game.rm.screen_to_ref(*pygame.mouse.get_pos())
        back_color = LIGHT_BLUE if self.back_button.collidepoint(mouse_pos) else BLUE
        reset_color = ORANGE if self.reset_button.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(screen, back_color, self.back_button, border_radius=8)
        pygame.draw.rect(screen, reset_color, self.reset_button, border_radius=8)
        back_text = self.font.render("RETOUR", True, WHITE)
        reset_text = self.font.render("REINITIALISER", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=self.back_button.center))
        screen.blit(reset_text, reset_text.get_rect(center=self.reset_button.center))
