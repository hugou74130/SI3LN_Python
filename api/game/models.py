from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Player(models.Model):
    """Player profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile', null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    total_score = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    highest_level = models.IntegerField(default=1)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, default='')
    bg_color = models.CharField(max_length=7, default='#000000')  # Hex color
    show_scores = models.BooleanField(default=True)
    boot_camp_completed = models.BooleanField(default=False)  # Boot Camp tutorial completion
    # Character unlock tracking
    unlocked_characters = models.JSONField(default=list, blank=True)  # List of unlocked character indices
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_score']

    def __str__(self):
        return self.username
    
    def unlock_character(self, character_idx):
        """Unlock a character if not already unlocked"""
        if character_idx not in self.unlocked_characters:
            self.unlocked_characters.append(character_idx)
            self.save(update_fields=['unlocked_characters'])
            return True
        return False
    
    def has_character_unlocked(self, character_idx):
        """Check if a character is unlocked"""
        return character_idx in self.unlocked_characters


class World(models.Model):
    """Game world/theme model"""
    WORLD_TYPES = [
        ('CLASSIC', 'Classic Space'),
        ('NEON', 'Neon City'),
        ('FOREST', 'Mystic Forest'),
        ('OCEAN', 'Deep Ocean'),
        ('DESERT', 'Mars Desert'),
    ]
    
    name = models.CharField(max_length=50, choices=WORLD_TYPES, unique=True)
    description = models.TextField(blank=True)
    background_color = models.CharField(max_length=7, default='#000000')  # Hex color
    difficulty_multiplier = models.FloatField(default=1.0)
    
    def __str__(self):
        return self.get_name_display()


class GameSession(models.Model):
    """Individual game session model"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sessions')
    world = models.ForeignKey(World, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.IntegerField(default=0)
    level_reached = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    enemies_killed = models.IntegerField(default=0)
    bullets_fired = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    duration_seconds = models.IntegerField(default=0)  # Game duration in seconds
    completed = models.BooleanField(default=False)
    is_tutorial = models.BooleanField(default=False)  # Boot Camp tutorial session
    tutorial_objectives_completed = models.IntegerField(default=0)  # Number of tutorial objectives done
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.player.username} - Level {self.level_reached} - Score {self.score}"

    def calculate_accuracy(self):
        """Calculate shooting accuracy percentage"""
        if self.bullets_fired > 0:
            self.accuracy = (self.enemies_killed / self.bullets_fired) * 100
        else:
            self.accuracy = 0.0
        return self.accuracy


class LeaderboardEntry(models.Model):
    """Persistent leaderboard entry with full historical tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='leaderboard_entries_v2')
    player_name = models.CharField(max_length=32, db_index=True, help_text="Denormalized for speed")
    score = models.IntegerField(default=0, db_index=True)
    world = models.ForeignKey(World, on_delete=models.SET_NULL, null=True, blank=True)
    level_id = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    character_used = models.CharField(max_length=32, default='')
    duration_sec = models.IntegerField(default=0)
    accuracy_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                       validators=[MinValueValidator(0), MaxValueValidator(100)])
    enemies_killed = models.IntegerField(default=0)
    powerups_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_pb = models.BooleanField(default=False, help_text="True if this run is a personal best")
    replay_hash = models.CharField(max_length=64, blank=True, default='',
                                   help_text="Deterministic hash of inputs for anti-cheat verification")
    verified = models.BooleanField(default=False, help_text="True if replay hash verified")
    flagged = models.BooleanField(default=False, help_text="True if score flagged for manual review")

    class Meta:
        ordering = ['-score', 'created_at']
        indexes = [
            models.Index(fields=['player', '-score']),
            models.Index(fields=['world', '-score']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"#{self.score} - {self.player_name} ({self.world.name if self.world else 'Any'})"

    def save(self, *args, **kwargs):
        """Auto-update player_name from player on creation"""
        if not self.player_name and self.player_id:
            self.player_name = self.player.username
        # Check if this is a personal best
        if not self._state.adding:
            # Only check PB on creation
            pass
        super().save(*args, **kwargs)
        if self._state.adding:
            self._update_pb_status()

    def _update_pb_status(self):
        """Mark this entry as PB if it's the player's highest score for this world/level"""
        from django.db.models import Max
        best = LeaderboardEntry.objects.filter(
            player=self.player,
            world=self.world,
            level_id=self.level_id
        ).aggregate(best=Max('score'))['best']
        if best is not None and self.score >= best:
            # Unmark previous PBs for this combo
            LeaderboardEntry.objects.filter(
                player=self.player,
                world=self.world,
                level_id=self.level_id,
                is_pb=True
            ).exclude(pk=self.pk).update(is_pb=False)
            self.is_pb = True
            LeaderboardEntry.objects.filter(pk=self.pk).update(is_pb=True)


class LeaderboardRank(models.Model):
    """Materialized view for leaderboard rankings (refreshed periodically)"""
    rank = models.IntegerField(primary_key=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='leaderboard_rank')
    player_name = models.CharField(max_length=32, db_index=True)
    best_score = models.IntegerField(default=0)
    total_runs = models.IntegerField(default=0)
    avg_score = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_played = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False  # Django won't create migrations for this; we use raw SQL
        db_table = 'leaderboard_ranks'
        ordering = ['rank']

    def __str__(self):
        return f"#{self.rank} - {self.player_name} (Best: {self.best_score})"


class Leaderboard(models.Model):
    """Legacy leaderboard entry model (kept for backward compatibility)"""
    PERIOD_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('ALL_TIME', 'All Time'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='leaderboard_entries_legacy')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    score = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    world = models.ForeignKey(World, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['period', 'rank']
        unique_together = ['player', 'period', 'world']

    def __str__(self):
        return f"#{self.rank} - {self.player.username} ({self.period})"


class Achievement(models.Model):
    """Achievement/Trophy model"""
    RARITY_CHOICES = [
        ('COMMON', 'Common'),
        ('RARE', 'Rare'),
        ('EPIC', 'Epic'),
        ('LEGENDARY', 'Legendary'),
    ]
    
    ACHIEVEMENT_TYPES = [
        ('GRADUATE', 'Boot Camp Graduate'),
        ('SCORE', 'Score Milestone'),
        ('LEVEL', 'Level Milestone'),
        ('ENEMIES', 'Enemies Killed'),
        ('WORLD', 'World Complete'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Icon identifier
    points = models.IntegerField(default=10)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='COMMON')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES, default='SCORE')
    requirement_type = models.CharField(max_length=50)  # e.g., 'score', 'level', 'enemies_killed'
    requirement_value = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name


class PlayerAchievement(models.Model):
    """Track player achievements"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    unlocked_at = models.DateTimeField(auto_now_add=True)  # Alias for compatibility
    
    class Meta:
        unique_together = ['player', 'achievement']
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.player.username} - {self.achievement.name}"


class PowerUp(models.Model):
    """Power-up types in the game"""
    POWERUP_TYPES = [
        ('SPEED', 'Speed Boost'),
        ('SHIELD', 'Shield'),
        ('DOUBLE_FIRE', 'Double Fire'),
        ('TRIPLE_FIRE', 'Triple Fire'),
        ('HEALTH', 'Extra Life'),
        ('SCORE_MULTIPLIER', 'Score Multiplier'),
    ]
    
    name = models.CharField(max_length=50, choices=POWERUP_TYPES, unique=True)
    description = models.TextField()
    duration_seconds = models.IntegerField(default=10)
    rarity = models.FloatField(default=1.0, validators=[MinValueValidator(0), MaxValueValidator(1)])  # 0-1, drop chance
    
    def __str__(self):
        return self.get_name_display()


class ScoreSubmissionLog(models.Model):
    """Rate-limiting log for anti-cheat"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='submission_logs')
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_hash = models.CharField(max_length=64, blank=True, default='',
                               help_text="Hashed IP for additional rate-limiting")
    score = models.IntegerField(default=0)
    accepted = models.BooleanField(default=True)
    rejection_reason = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['player', '-submitted_at']),
        ]

    def __str__(self):
        return f"{self.player.username} @ {self.submitted_at} - {'OK' if self.accepted else 'REJECTED'}"
