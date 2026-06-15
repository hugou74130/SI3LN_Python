from ninja import Schema
from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator
import re


class PlayerSchema(Schema):
    id: int
    username: str
    email: Optional[str] = ""
    total_score: int
    games_played: int
    highest_level: int
    boot_camp_completed: bool = False
    unlocked_characters: list = []
    created_at: datetime


class PlayerCharacterUnlockSchema(Schema):
    character_idx: int
    success: bool
    message: str


class PlayerAchievementGrantSchema(Schema):
    achievement_name: str
    success: bool
    message: str


class PlayerCreateSchema(Schema):
    username: str
    email: str


class GameSessionSchema(Schema):
    id: int
    player_id: int
    world_id: Optional[int] = None
    score: int
    level_reached: int
    enemies_killed: int
    duration_seconds: int
    completed: bool
    is_tutorial: bool = False
    tutorial_objectives_completed: int = 0
    started_at: datetime
    ended_at: Optional[datetime] = None


class GameSessionCreateSchema(Schema):
    player_id: int
    world_id: Optional[int] = None


class GameSessionUpdateSchema(Schema):
    score: Optional[int] = Field(None, ge=0)
    level_reached: Optional[int] = None
    enemies_killed: Optional[int] = None
    duration_seconds: Optional[int] = None
    completed: Optional[bool] = None
    is_tutorial: Optional[bool] = None
    tutorial_objectives_completed: Optional[int] = None
    ended_at: Optional[datetime] = None


class LeaderboardEntrySchema(Schema):
    rank: int
    player_id: int
    player_username: str
    score: int
    level_reached: int
    world_name: Optional[str] = None
    created_at: datetime


class MessageSchema(Schema):
    message: str


class UserSchema(Schema):
    """
    User schema that explicitly excludes password field
    to prevent accidental password hash exposure in API responses
    """
    id: int
    username: str
    email: Optional[str] = ""
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    is_active: bool
    date_joined: datetime
    
    class Config:
        # Explicitly exclude password and other sensitive fields
        exclude = ['password', 'last_login']


# World Schemas
class WorldSchema(Schema):
    id: int
    name: str
    description: Optional[str] = ""
    background_color: str
    difficulty_multiplier: float


# Achievement Schemas
class AchievementSchema(Schema):
    id: int
    name: str
    description: str
    icon: Optional[str] = ""
    points: int
    rarity: str
    requirement_type: str
    requirement_value: int


class PlayerAchievementSchema(Schema):
    id: int
    achievement: AchievementSchema
    earned_at: datetime
    unlocked_at: datetime


# Enhanced Profile Schemas
class EnhancedProfileSchema(Schema):
    id: int
    username: str
    email: Optional[str] = ""
    total_score: int
    games_played: int
    highest_level: int
    boot_camp_completed: bool = False
    avatar_url: Optional[str] = None
    bio: Optional[str] = ""
    bg_color: Optional[str] = "#000000"
    show_scores: bool = True
    unlocked_characters: list = []
    created_at: datetime
    updated_at: datetime
    achievements_count: int
    recent_achievements: list = []


class ProfileUpdateSchema(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    bg_color: Optional[str] = None
    show_scores: Optional[bool] = None

    @field_validator('bg_color')
    @classmethod
    def validate_bg_color(cls, v):
        if v is not None and not re.match(r'^#[0-9a-fA-F]{6}$', v):
            raise ValueError('Invalid hex color. Use format like #FF5500.')
        return v


# Tutorial/Boot Camp Schemas
class BootCampStatusSchema(Schema):
    boot_camp_completed: bool
    graduate_badge: bool = False
    worlds_unlocked: list = []

class BootCampCompleteSchema(Schema):
    message: str
    graduate_badge: bool = True
    space_unlocked: bool = True

class TutorialProgressSchema(Schema):
    objectives_completed: int
    total_objectives: int = 5
    current_objective: Optional[str] = None
    completed: bool = False

class TutorialObjectiveSchema(Schema):
    obj_type: str
    description: str
    target_value: int
    current_value: int = 0
    completed: bool = False

class ChangePasswordSchema(Schema):
    old_password: str
    new_password: str


# Account Update Schema
class AccountUpdateSchema(Schema):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# ── Leaderboard v2 Schemas ────────────────────────────────────────────

class LeaderboardEntryDetailSchema(Schema):
    """Full leaderboard entry response"""
    id: str
    player_id: int
    player_name: str
    score: int
    world_id: Optional[int] = None
    level_id: int
    character_used: str
    duration_sec: int
    accuracy_pct: float
    enemies_killed: int
    powerups_used: int
    created_at: datetime
    is_pb: bool
    verified: bool


class LeaderboardRankSchema(Schema):
    """Materialized view rank entry"""
    rank: int
    player_id: int
    player_name: str
    best_score: int
    total_runs: int
    avg_score: float
    last_played: Optional[datetime] = None


class LeaderboardSubmitSchema(Schema):
    """Request body for submitting a new run"""
    score: int = Field(..., ge=0, description="Final score for the run")
    world_id: int = Field(..., ge=1, description="World ID played")
    level_id: int = Field(..., ge=1, description="Level reached")
    character_used: str = Field(default="", max_length=32)
    duration_sec: int = Field(default=0, ge=0)
    accuracy_pct: float = Field(default=0.0, ge=0, le=100)
    enemies_killed: int = Field(default=0, ge=0)
    powerups_used: int = Field(default=0, ge=0)
    bullets_fired: int = Field(default=0, ge=0)
    replay_hash: str = Field(default="", max_length=64, description="Deterministic hash of inputs")
    session_id: Optional[int] = Field(default=None, description="Optional linked GameSession ID")

    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        if v > 9_999_999:
            raise ValueError('Score exceeds maximum possible value')
        return v


class LeaderboardGlobalResponseSchema(Schema):
    """Response for global leaderboard query"""
    entries: list[LeaderboardEntryDetailSchema]
    total: int
    world_id: Optional[int] = None


class LeaderboardPlayerHistorySchema(Schema):
    """Response for player history + PBs"""
    player_id: int
    player_name: str
    personal_bests: list[LeaderboardEntryDetailSchema]
    recent_runs: list[LeaderboardEntryDetailSchema]
    total_runs: int
    avg_score: float
    best_score: int


class LeaderboardNearbySchema(Schema):
    """Response for nearby ranks"""
    target_player_id: int
    target_rank: int
    entries: list[LeaderboardRankSchema]


class LeaderboardSubmitResponseSchema(Schema):
    """Response after score submission"""
    success: bool
    entry_id: Optional[str] = None
    is_pb: bool = False
    new_rank: Optional[int] = None
    message: str
    flagged: bool = False
