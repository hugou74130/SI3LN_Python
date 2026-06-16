"""
Game entities: Player, Enemy, Bullet
"""
import pygame
import random
import math
from constants import *


class Player(pygame.sprite.Sprite):
    """Player entity with Phase Dash ability support"""
    def __init__(self, x, y, image, screen_width, screen_height, character_idx=0, keybinding_manager=None, sound_manager=None):
        super().__init__()
        self.image = image
        self.original_image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = PLAYER_SPEED
        self.character_idx = character_idx
        self.keybinding = keybinding_manager
        self.sound = sound_manager
        
        # Play area boundaries (keep player in visible area)
        self.min_x = 0
        self.max_x = screen_width
        self.min_y = screen_height // 2  # Can't go above middle
        self.max_y = screen_height - 20

        # ── Shield / Protection system ────────────────────────────────────
        self.max_shield = 100
        self.shield = 0
        self.shield_active = False
        self.shield_start_time = 0
        self.shield_duration_ms = 3000  # 3 seconds of active protection

        # ── Phase Dash ability (Phantom Striker - character 7) ───────────
        self.is_phantom = (character_idx == 7)
        self.phase_dash = {
            "active": False,
            "cooldown": False,
            "dash_start_time": 0,
            "cooldown_start_time": 0,
            "dash_duration_ms": 500,   # 0.5s invincibility
            "cooldown_ms": 8000,       # 8s cooldown
            "speed_multiplier": 2.5,   # 2.5x speed during dash
            "invincible": False,
        }
        # Ghost trail effect for Phase Dash
        self.ghost_trail = []  # List of (image_copy, rect_copy, alpha)
    
    def move(self, dx, dy):
        """Move player with boundary checking"""
        # Apply speed multiplier during Phase Dash
        speed = self.speed
        if self.is_phantom and self.phase_dash["active"]:
            speed = int(self.speed * self.phase_dash["speed_multiplier"])
        
        self.rect.x += dx * speed
        self.rect.y += dy * speed
        
        # Keep within boundaries
        self.rect.x = max(self.min_x, min(self.rect.x, self.max_x - self.rect.width))
        self.rect.y = max(self.min_y, min(self.rect.y, self.max_y - self.rect.height))
    
    def update(self, keys):
        """Update player based on key presses"""
        dx = 0
        dy = 0

        if self.keybinding is not None:
            if self.keybinding.is_pressed(keys, "move_left"):
                dx = -1
            if self.keybinding.is_pressed(keys, "move_right"):
                dx = 1
            if self.keybinding.is_pressed(keys, "move_up"):
                dy = -1
            if self.keybinding.is_pressed(keys, "move_down"):
                dy = 1
        else:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

        # Phase Dash activation (Phantom Striker only)
        dash_pressed = False
        if self.keybinding is not None:
            dash_pressed = self.keybinding.is_pressed(keys, "phase_dash")
        else:
            dash_pressed = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        if self.is_phantom and dash_pressed:
            self.trigger_phase_dash()
        
        # Update Phase Dash state
        self._update_phase_dash()
        
        if dx != 0 or dy != 0:
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
            self.move(dx, dy)
            
            # Update ghost trail during dash
            if self.is_phantom and self.phase_dash["active"]:
                self._update_ghost_trail()

    def trigger_phase_dash(self):
        """Activate Phase Dash if not on cooldown"""
        if not self.phase_dash["active"] and not self.phase_dash["cooldown"]:
            self.phase_dash["active"] = True
            self.phase_dash["invincible"] = True
            self.phase_dash["dash_start_time"] = pygame.time.get_ticks()
            # Visual effect: make player semi-transparent
            self._set_transparency(180)
            if self.sound:
                self.sound.play("dash")
    
    def _update_phase_dash(self):
        """Update Phase Dash timers and state"""
        if not self.is_phantom:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Check if dash duration expired
        if self.phase_dash["active"]:
            elapsed = current_time - self.phase_dash["dash_start_time"]
            if elapsed >= self.phase_dash["dash_duration_ms"]:
                # End dash, start cooldown
                self.phase_dash["active"] = False
                self.phase_dash["invincible"] = False
                self.phase_dash["cooldown"] = True
                self.phase_dash["cooldown_start_time"] = current_time
                # Restore normal opacity
                self._set_transparency(255)
                # Clear ghost trail
                self.ghost_trail.clear()
        
        # Check if cooldown expired
        if self.phase_dash["cooldown"]:
            elapsed = current_time - self.phase_dash["cooldown_start_time"]
            if elapsed >= self.phase_dash["cooldown_ms"]:
                self.phase_dash["cooldown"] = False
    
    def _set_transparency(self, alpha):
        """Set player image transparency"""
        if self.original_image:
            self.image = self.original_image.copy()
            self.image.set_alpha(alpha)
    
    def _update_ghost_trail(self):
        """Update ghost trail effect during Phase Dash"""
        # Add current position to trail
        ghost = {
            "rect": self.rect.copy(),
            "alpha": 150,
        }
        self.ghost_trail.insert(0, ghost)
        
        # Fade out old trail entries
        for ghost in self.ghost_trail:
            ghost["alpha"] -= 20
        
        # Remove fully faded entries
        self.ghost_trail = [g for g in self.ghost_trail if g["alpha"] > 0]
        
        # Limit trail length
        if len(self.ghost_trail) > 5:
            self.ghost_trail = self.ghost_trail[:5]
    
    def get_phase_dash_cooldown_ratio(self):
        """Return cooldown progress as 0.0 (ready) to 1.0 (full cooldown)"""
        if not self.is_phantom:
            return 0.0
        if self.phase_dash["cooldown"]:
            elapsed = pygame.time.get_ticks() - self.phase_dash["cooldown_start_time"]
            return min(1.0, elapsed / self.phase_dash["cooldown_ms"])
        return 0.0
    
    def is_invincible(self):
        """Check if player is currently invincible (Phase Dash)"""
        return self.is_phantom and self.phase_dash["invincible"]

    def activate_shield(self):
        """Activate the protection shield at full charge."""
        self.shield = self.max_shield
        self.shield_active = True
        self.shield_start_time = pygame.time.get_ticks()

    def update_shield(self):
        """Update shield timer and deactivate when expired."""
        if not self.shield_active:
            return
        elapsed = pygame.time.get_ticks() - self.shield_start_time
        if elapsed >= self.shield_duration_ms:
            self.shield_active = False
            self.shield = 0

    def take_damage(self, damage):
        """Apply damage to shield first, then to the caller-managed lives.
        Returns the remaining damage that should be subtracted from lives."""
        if self.shield_active and self.shield > 0:
            absorbed = min(self.shield, damage)
            self.shield -= absorbed
            damage -= absorbed
            if self.shield <= 0:
                self.shield_active = False
        return damage

    def is_shielded(self):
        """Return True if the player currently has active shield protection."""
        return self.shield_active and self.shield > 0

    def get_shield_ratio(self):
        """Return shield charge ratio from 0.0 to 1.0."""
        if self.max_shield <= 0:
            return 0.0
        return self.shield / self.max_shield

    def move_toward(self, target_x, target_y):
        """Move player toward a target point (used by touch controls).
        The player follows the finger but stops when close enough."""
        cx, cy = self.rect.centerx, self.rect.centery
        diff_x = target_x - cx
        diff_y = target_y - cy
        dist = (diff_x ** 2 + diff_y ** 2) ** 0.5
        if dist < 4:
            return  # Close enough, don't jitter
        # Normalize and apply speed
        dx = diff_x / dist
        dy = diff_y / dist
        self.move(dx, dy)


class Enemy(pygame.sprite.Sprite):
    """Enemy entity"""
    def __init__(self, x, y, image, screen_width, level=1, harmless=False, can_shoot=True, behavior="normal"):
        super().__init__()
        self.image = image
        self.original_image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.screen_width = screen_width
        
        # Mode flags
        self.harmless = harmless
        self.can_shoot_flag = can_shoot
        self.behavior = behavior  # "normal" (space invaders) or "patrol" (horizontal only)
        
        # Movement
        self.speed = ENEMY_SPEED + (level * 0.2)
        if harmless:
            self.speed *= 0.6  # Slower for tutorial targets
        self.direction = 1
        self.drop_distance = 20
        
        # Shooting
        self.last_shot = pygame.time.get_ticks()
        self.shoot_cooldown = max(700, 3000 - level * 100)  # Faster shooting at higher levels
        self.shoot_chance = min(0.1 * level, 0.5)  # Max 15% chance per frame
        
        # Boundaries (enemy play area)
        self.min_x = 20
        self.max_x = screen_width - 20
        self.max_y = screen_width // 2  # Don't go too low
    
    def update(self):
        """Update enemy position"""
        # Horizontal movement
        self.rect.x += self.speed * self.direction
        
        # Boundary checking and direction change
        if self.rect.right >= self.max_x and self.direction > 0:
            self.direction = -1
            if self.behavior != "patrol":
                self.rect.y += self.drop_distance
        elif self.rect.left <= self.min_x and self.direction < 0:
            self.direction = 1
            if self.behavior != "patrol":
                self.rect.y += self.drop_distance
        
        # Keep within vertical bounds
        if self.rect.bottom > self.max_y:
            self.rect.bottom = self.max_y
    
    def can_shoot(self):
        """Check if enemy can shoot"""
        if self.harmless or not self.can_shoot_flag:
            return False
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            if random.random() < self.shoot_chance:
                self.last_shot = current_time
                return True
        return False


class Bullet(pygame.sprite.Sprite):
    """Bullet entity"""
    def __init__(self, x, y, image, is_player_bullet, screen_height):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.is_player_bullet = is_player_bullet
        self.screen_height = screen_height
        
        if is_player_bullet:
            self.speed = -PLAYER_BULLET_SPEED  # Negative = upward
        else:
            self.speed = ENEMY_BULLET_SPEED  # Positive = downward
    
    def update(self):
        """Update bullet position"""
        self.rect.y += self.speed
        
        # Remove if off screen
        if self.rect.bottom < 0 or self.rect.top > self.screen_height:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """Simple explosion effect"""
    def __init__(self, x, y, color=ORANGE, explosion_img=None):
        super().__init__()
        self.frames = []
        
        if explosion_img:
            # Use provided explosion image with scaling animation
            for scale in [0.3, 0.6, 1.0, 0.8, 0.5, 0.2]:
                w, h = explosion_img.get_size()
                new_w = int(w * scale)
                new_h = int(h * scale)
                if new_w > 0 and new_h > 0:
                    surf = pygame.transform.scale(explosion_img, (new_w, new_h))
                    self.frames.append(surf)
        else:
            # Create explosion animation frames with circles (fallback)
            for size in [10, 20, 30, 25, 15, 5]:
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size, size), size)
                self.frames.append(surf)
        
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 3
        self.counter = 0
    
    def update(self):
        """Update explosion animation"""
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                self.kill()
            else:
                old_center = self.rect.center
                self.image = self.frames[self.current_frame]
                self.rect = self.image.get_rect(center=old_center)


class Waypoint(pygame.sprite.Sprite):
    """Tutorial waypoint marker - player must move here"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        
        # Draw pulsing ring
        pygame.draw.circle(self.image, HOLO_BLUE, (30, 30), 25, 3)
        pygame.draw.circle(self.image, HOLO_GREEN, (30, 30), 15, 2)
        
        # Draw arrow pointing up
        pygame.draw.polygon(self.image, HOLO_GREEN, [
            (30, 10), (20, 25), (40, 25)
        ])
        
        self.rect = self.image.get_rect(center=(x, y))
        self.base_image = self.image.copy()
        self.pulse_timer = 0
        self.pulse_speed = 0.08
        self.base_scale = 1.0
    
    def update(self):
        """Pulse animation using a pre-rendered base image"""
        self.pulse_timer += self.pulse_speed
        scale = self.base_scale + 0.1 * math.sin(self.pulse_timer)
        scale = max(0.8, min(1.2, scale))  # Clamp between 0.8 and 1.2
        
        new_size = max(1, int(60 * scale))
        self.image = pygame.transform.scale(self.base_image, (new_size, new_size))
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)


class ExitPortal(pygame.sprite.Sprite):
    """Exit portal for tutorial completion"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        
        # Draw portal - swirling vortex effect
        pygame.draw.circle(self.image, HOLO_BLUE, (40, 40), 35, 4)
        pygame.draw.circle(self.image, HOLO_GREEN, (40, 40), 25, 3)
        pygame.draw.circle(self.image, WHITE, (40, 40), 15, 2)
        
        # Draw exit arrow
        pygame.draw.polygon(self.image, WHITE, [
            (40, 15), (25, 35), (55, 35)
        ])
        
        self.rect = self.image.get_rect(center=(x, y))
        self.rotation = 0
        self.rotation_speed = 2
        self.base_image = self.image.copy()
    
    def update(self):
        """Rotate portal animation"""
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)


class TutorialObjective:
    """Represents a single tutorial objective"""
    def __init__(self, obj_type, target_value, description):
        self.type = obj_type
        self.target_value = target_value
        self.current_value = 0
        self.description = description
        self.completed = False
        self.announced = False  # Track if completion was announced
    
    def update(self, value):
        """Update progress and check completion"""
        self.current_value = value
        if self.current_value >= self.target_value and not self.completed:
            self.completed = True
            return True  # Just completed
        return False
    
    def get_progress_text(self):
        """Get progress display text"""
        if self.type == TUTORIAL_OBJ_MOVE:
            return f"{self.description}: {min(self.current_value, self.target_value)}/{self.target_value}m"
        elif self.type == TUTORIAL_OBJ_SHOOT:
            return f"{self.description}: {min(self.current_value, self.target_value)}/{self.target_value}"
        elif self.type == TUTORIAL_OBJ_COLLECT:
            return f"{self.description}: {'✓' if self.completed else '...'}"
        elif self.type == TUTORIAL_OBJ_SURVIVE:
            remaining = max(0, self.target_value - self.current_value)
            return f"{self.description}: {remaining//1000}s"
        elif self.type == TUTORIAL_OBJ_EXIT:
            return f"{self.description}: {'✓' if self.completed else '...'}"
        return self.description


class PowerUp(pygame.sprite.Sprite):
    """Power-up collectible (future feature)"""
    def __init__(self, x, y, power_type="health"):
        super().__init__()
        self.power_type = power_type
        
        # Create visual
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        color = GREEN if power_type == "health" else CYAN
        pygame.draw.circle(self.image, color, (15, 15), 15)
        pygame.draw.circle(self.image, WHITE, (15, 15), 15, 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
    
    def update(self):
        """Move power-up down"""
        self.rect.y += self.speed
        if self.rect.top > 800:  # Off screen
            self.kill()

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, bonus_type):
        super().__init__()
        self.bonus_type = bonus_type  # "life", "shield", "mega_shot"
        self.colors = {
            "life": RED, 
            "shield": BLUE, 
            "mega_shot": YELLOW
        }
        self.symbols = {
            "life": "♥",
            "shield": "⛊", 
            "mega_shot": "⚡"
        }

        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.colors[bonus_type], (15, 15), 15)
        pygame.draw.circle(self.image, WHITE, (15, 15), 12, 2)

        font = pygame.font.Font(None, 20)
        symbol = font.render(self.symbols[bonus_type], True, WHITE)
        symbol_rect = symbol.get_rect(center=(15, 15))
        self.image.blit(symbol, symbol_rect)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()

class SpecialAttack(pygame.sprite.Sprite):
    def __init__(self, attack_type, world, level, screen_width, screen_height):
        super().__init__()
        self.attack_type = attack_type
        self.world = world
        self.level = level
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.duration = min(2000 + (level * 200), 4000)  # 4s
        self.damage = 1 + (level // 3)  # Damage dealt on player contact
        
        if world == "Space":
            # Laser
            self.image = pygame.Surface((10, screen_height))
            self.image.fill(PURPLE)
            self.rect = self.image.get_rect(center=(random.randint(50, screen_width-50), 0))
            self.speed = 5
            
        elif world == "Desert":
            # Sand
            self.image = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            self.image.fill((210, 180, 140, 180))
            self.rect = self.image.get_rect(topleft=(0, 0))
            
        elif world == "Forest":
            # Roots
            self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (139, 69, 19), (40, 40), 40)
            pygame.draw.circle(self.image, (101, 67, 33), (40, 40), 30)
            self.rect = self.image.get_rect(center=(screen_width//2, screen_height-50))
            
        elif world == "Marine":
            # Ice ball
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (173, 216, 230), (20, 20), 20)
            pygame.draw.circle(self.image, (135, 206, 235), (20, 20), 15)
            self.rect = self.image.get_rect(center=(random.randint(50, screen_width-50), 0))
            self.speed = 3
            
        elif world == "Apocalyptic":
            # Enery Ball
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 255, 0), (25, 25), 25)
            pygame.draw.circle(self.image, (255, 165, 0), (25, 25), 15)
            self.rect = self.image.get_rect(center=(random.randint(50, screen_width-50), 0))
            self.speed_x = random.choice([-3, 3])
            self.speed_y = 4
            self.bounces = 0
            self.max_bounces = 3
    
    def update(self):
        if self.world == "Space":
            self.rect.y += self.speed
            if self.rect.top > self.screen_height:
                self.kill()
                
        elif self.world == "Marine":
            self.rect.y += self.speed
            if self.rect.top > self.screen_height:
                self.kill()
                
        elif self.world == "Apocalyptic":
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

            if self.rect.left <= 0 or self.rect.right >= self.screen_width:
                self.speed_x = -self.speed_x
                self.bounces += 1
            if self.rect.top <= 0:
                self.speed_y = -self.speed_y
                self.bounces += 1
                
            if self.bounces >= self.max_bounces or self.rect.top > self.screen_height:
                self.kill()
