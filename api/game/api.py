from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from django.db import connection
from django.utils import timezone
from django.db.models import Max, Avg, Count, Q
from .models import Player, GameSession, LeaderboardEntry, LeaderboardRank, ScoreSubmissionLog, World
from .schemas import (
    PlayerSchema,
    PlayerCreateSchema,
    GameSessionSchema,
    GameSessionCreateSchema,
    GameSessionUpdateSchema,
    LeaderboardEntrySchema,
    LeaderboardEntryDetailSchema,
    LeaderboardRankSchema,
    LeaderboardSubmitSchema,
    LeaderboardGlobalResponseSchema,
    LeaderboardPlayerHistorySchema,
    LeaderboardNearbySchema,
    LeaderboardSubmitResponseSchema,
    MessageSchema,
    WorldSchema,
    AchievementSchema,
    PlayerAchievementSchema,
    EnhancedProfileSchema,
    ProfileUpdateSchema,
    BootCampStatusSchema,
    BootCampCompleteSchema,
    TutorialProgressSchema,
)
from .auth.auth_decorators import jwt_auth

router = Router()


# ── Anti-cheat helpers ───────────────────────────────────────────────

MAX_SCORE_PER_ENEMY = 150
MAX_SCORE_PER_LEVEL_BONUS = 5000
MAX_SCORE_PER_POWERUP = 1000
RATE_LIMIT_SECONDS = 10


def _get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _hash_ip(ip: str) -> str:
    """Hash IP address for privacy-compliant rate limiting."""
    import hashlib
    return hashlib.sha256(ip.encode()).hexdigest()[:32]


def _check_rate_limit(player: Player, ip_hash: str) -> tuple[bool, str]:
    """Check if player is rate-limited. Returns (allowed, reason)."""
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(seconds=RATE_LIMIT_SECONDS)
    recent = ScoreSubmissionLog.objects.filter(
        Q(player=player) | Q(ip_hash=ip_hash),
        submitted_at__gte=cutoff
    ).first()
    if recent:
        remaining = RATE_LIMIT_SECONDS - (timezone.now() - recent.submitted_at).seconds
        return False, f"Rate limited. Wait {remaining}s before next submission."
    return True, ""


def _validate_max_possible_score(score: int, enemies_killed: int, level_id: int,
                                  powerups_used: int, bullets_fired: int) -> tuple[bool, str]:
    """Server-side score validation: compute theoretical max and reject impossibly high scores."""
    max_from_enemies = enemies_killed * MAX_SCORE_PER_ENEMY
    max_level_bonus = (level_id - 1) * MAX_SCORE_PER_LEVEL_BONUS
    max_from_powerups = powerups_used * MAX_SCORE_PER_POWERUP
    # Add generous headroom (2x) for combo multipliers / bonuses
    theoretical_max = (max_from_enemies + max_level_bonus + max_from_powerups) * 2
    if score > theoretical_max:
        return False, (
            f"Score {score} exceeds theoretical maximum {theoretical_max} "
            f"(enemies={enemies_killed}, level={level_id}, powerups={powerups_used})"
        )
    # Sanity: accuracy consistency
    if bullets_fired > 0:
        expected_accuracy = (enemies_killed / bullets_fired) * 100
        # Allow 10% margin for splash damage / multi-kills
        if expected_accuracy > 110:
            return False, f"Accuracy inconsistency: {expected_accuracy:.1f}% with {bullets_fired} bullets fired"
    return True, ""


def _verify_replay_hash(replay_hash: str, score: int, enemies_killed: int,
                        duration_sec: int, level_id: int) -> bool:
    """Verify replay hash determinism. Simple heuristic: hash must be non-empty and look valid."""
    if not replay_hash or len(replay_hash) < 16:
        return False
    # In a full implementation, the server would replay the inputs and compare.
    # For now we accept any well-formed hash and flag for manual review if suspicious.
    return True


def _refresh_leaderboard_ranks():
    """Refresh the materialized view leaderboard_ranks."""
    with connection.cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS leaderboard_ranks;
            CREATE TABLE leaderboard_ranks AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY MAX(le.score) DESC) AS rank,
                p.id AS player_id,
                p.username AS player_name,
                MAX(le.score) AS best_score,
                COUNT(le.id) AS total_runs,
                ROUND(AVG(le.score), 2) AS avg_score,
                MAX(le.created_at) AS last_played
            FROM game_leaderboardentry le
            JOIN game_player p ON le.player_id = p.id
            WHERE le.verified = TRUE AND le.flagged = FALSE
            GROUP BY p.id, p.username
            ORDER BY best_score DESC;
        """)


def _entry_to_dict(entry: LeaderboardEntry) -> dict:
    """Serialize a LeaderboardEntry to a dict matching LeaderboardEntryDetailSchema."""
    return {
        "id": str(entry.id),
        "player_id": entry.player_id,
        "player_name": entry.player_name,
        "score": entry.score,
        "world_id": entry.world_id,
        "level_id": entry.level_id,
        "character_used": entry.character_used,
        "duration_sec": entry.duration_sec,
        "accuracy_pct": float(entry.accuracy_pct),
        "enemies_killed": entry.enemies_killed,
        "powerups_used": entry.powerups_used,
        "created_at": entry.created_at,
        "is_pb": entry.is_pb,
        "verified": entry.verified,
    }


# Player endpoints (protected)
@router.get("/players", response=List[PlayerSchema], tags=["Players"], auth=jwt_auth)
def list_players(request, limit: int = 50, offset: int = 0):
    """Get players with optional pagination (requires authentication).

    * `limit` – maximum number of players to return (default 50).
    * `offset` – number of players to skip (default 0).
    """
    qs = Player.objects.all().order_by("id")
    # enforce sensible bounds to avoid overloading the database
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200
    if offset < 0:
        offset = 0
    return qs[offset : offset + limit]


@router.post("/players", response=PlayerSchema, tags=["Players"])
def create_player(request, payload: PlayerCreateSchema):
    """Create a new player (public for game registration)"""
    player = Player.objects.create(**payload.dict())
    return player


@router.get("/players/{player_id}", response=PlayerSchema, tags=["Players"], auth=jwt_auth)
def get_player(request, player_id: int):
    """Get a specific player by ID (requires authentication)"""
    return get_object_or_404(Player, id=player_id)


@router.put("/players/{player_id}", response=PlayerSchema, tags=["Players"], auth=jwt_auth)
def update_player(request, player_id: int, payload: PlayerCreateSchema):
    """Update a player (requires authentication — can only update own player)"""
    from ninja.responses import Response
    player = get_object_or_404(Player, id=player_id)
    if player.user != request.auth:
        return Response({"error": "You can only update your own player."}, status=403)
    for attr, value in payload.dict().items():
        setattr(player, attr, value)
    player.save()
    return player


@router.delete("/players/{player_id}", response=MessageSchema, tags=["Players"], auth=jwt_auth)
def delete_player(request, player_id: int):
    """Delete a player (requires authentication — can only delete own player)"""
    from ninja.responses import Response
    player = get_object_or_404(Player, id=player_id)
    if player.user != request.auth:
        return Response({"error": "You can only delete your own player."}, status=403)
    player.delete()
    return {"message": "Player deleted successfully"}


# Game Session endpoints (protected)
@router.get("/sessions", response=List[GameSessionSchema], tags=["Game Sessions"], auth=jwt_auth)
def list_sessions(
    request,
    player_id: int = None,
    world_id: int = None,
    limit: int = 50,
    offset: int = 0,
):
    """Get game sessions with optional pagination (requires authentication).

    Filtering by `player_id` or `world_id` is still supported.
    ``limit`` and ``offset`` work just like on ``/players``.
    """
    sessions = GameSession.objects.all()
    if player_id:
        sessions = sessions.filter(player_id=player_id)
    if world_id:
        sessions = sessions.filter(world_id=world_id)
    sessions = sessions.order_by("-started_at")
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200
    if offset < 0:
        offset = 0
    return sessions[offset : offset + limit]


@router.post("/sessions", response=GameSessionSchema, tags=["Game Sessions"], auth=jwt_auth)
def create_session(request, payload: GameSessionCreateSchema):
    """Create a new game session (requires authentication)"""
    # Validate player exists
    player = Player.objects.filter(id=payload.player_id).first()
    if player is None:
        from ninja.responses import Response
        return Response({"error": f"Player with id {payload.player_id} does not exist."}, status=404)
    if player.user != request.auth:
        from ninja.responses import Response
        return Response({"error": "You can only create sessions for your own players."}, status=403)
    session = GameSession.objects.create(**payload.dict())
    return session


@router.get("/sessions/{session_id}", response=GameSessionSchema, tags=["Game Sessions"], auth=jwt_auth)
def get_session(request, session_id: int):
    """Get a specific game session (requires authentication)"""
    return get_object_or_404(GameSession, id=session_id)


@router.patch("/sessions/{session_id}", response=GameSessionSchema, tags=["Game Sessions"], auth=jwt_auth)
def update_session(request, session_id: int, payload: GameSessionUpdateSchema):
    """Update a game session (requires authentication)"""
    from django.utils import timezone
    session = get_object_or_404(GameSession, id=session_id)
    if session.player.user != request.auth:
        from ninja.responses import Response
        return Response({"error": "You can only update your own sessions."}, status=403)

    # Validate level_reached >= 1
    if payload.level_reached is not None and payload.level_reached < 1:
        from ninja.responses import Response
        return Response({"error": "level_reached must be at least 1."}, status=400)

    # Remember completion state BEFORE applying updates (prevent double-counting)
    was_completed = session.completed

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(session, attr, value)

    # Auto-set ended_at when session is first marked completed
    if payload.completed and not session.ended_at:
        session.ended_at = timezone.now()

    session.save()

    # Update player stats ONLY on the FIRST completion (not on subsequent patches)
    if payload.completed and not was_completed and payload.score is not None:
        player = session.player
        player.total_score += payload.score
        player.games_played += 1
        if payload.level_reached is not None and payload.level_reached > player.highest_level:
            player.highest_level = payload.level_reached
        player.save()

    return session


@router.delete("/sessions/{session_id}", response=MessageSchema, tags=["Game Sessions"], auth=jwt_auth)
def delete_session(request, session_id: int):
    """Delete a game session (requires authentication)"""
    session = get_object_or_404(GameSession, id=session_id)
    if session.player.user != request.auth:
        from ninja.responses import Response
        return Response({"error": "You can only delete your own sessions."}, status=403)
    session.delete()
    return {"message": "Session deleted successfully"}


# ── Legacy Leaderboard endpoints (public - kept for backward compatibility) ──
@router.get("/leaderboard", response=List[LeaderboardEntrySchema], tags=["Leaderboard"])
def get_leaderboard(request, world_id: int = None, limit: int = 10):
    """Get the legacy leaderboard (public access) — kept for backward compatibility."""
    sessions = GameSession.objects.select_related("player", "world")
    
    if world_id:
        sessions = sessions.filter(world_id=world_id)
    
    sessions = sessions.order_by("-score")[:limit]
    
    leaderboard = []
    for rank, session in enumerate(sessions, start=1):
        leaderboard.append({
            "rank": rank,
            "player_id": session.player.id,
            "player_username": session.player.username,
            "score": session.score,
            "level_reached": session.level_reached,
            "world_name": session.world.name if session.world else None,
            "created_at": session.started_at,
        })
    
    return leaderboard


# ── Leaderboard v2 endpoints ─────────────────────────────────────────

@router.get("/leaderboard/global", response=LeaderboardGlobalResponseSchema, tags=["Leaderboard v2"])
def get_leaderboard_global(request, world: int = None, limit: int = 50):
    """Get top N global scores from the persistent leaderboard.

    * `world` – filter by world ID (optional).
    * `limit` – max entries to return (default 50, max 200).
    """
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200

    qs = LeaderboardEntry.objects.filter(verified=True, flagged=False)
    if world is not None:
        qs = qs.filter(world_id=world)

    total = qs.count()
    entries = qs.order_by("-score", "created_at")[:limit]

    return {
        "entries": [_entry_to_dict(e) for e in entries],
        "total": total,
        "world_id": world,
    }


@router.get("/leaderboard/player/{player_id}", response=LeaderboardPlayerHistorySchema, tags=["Leaderboard v2"])
def get_leaderboard_player(request, player_id: int):
    """Get a player's full history + personal bests."""
    player = get_object_or_404(Player, id=player_id)
    all_entries = LeaderboardEntry.objects.filter(player=player).order_by("-created_at")
    pbs = all_entries.filter(is_pb=True).order_by("-score")
    recent = all_entries[:20]

    stats = all_entries.aggregate(
        best=Max("score"),
        avg=Avg("score"),
        total=Count("id"),
    )

    return {
        "player_id": player.id,
        "player_name": player.username,
        "personal_bests": [_entry_to_dict(e) for e in pbs],
        "recent_runs": [_entry_to_dict(e) for e in recent],
        "total_runs": stats.get("total", 0),
        "avg_score": round(float(stats.get("avg") or 0), 2),
        "best_score": stats.get("best") or 0,
    }


@router.get("/leaderboard/nearby", response=LeaderboardNearbySchema, tags=["Leaderboard v2"])
def get_leaderboard_nearby(request, player: int, radius: int = 5):
    """Get players ranked near the target player.

    * `player` – target player ID.
    * `radius` – how many ranks above and below to include (default 5, max 20).
    """
    if radius < 1:
        radius = 1
    if radius > 20:
        radius = 20

    # Find target player's rank from materialized view
    target_rank = None
    try:
        rank_entry = LeaderboardRank.objects.filter(player_id=player).first()
        if rank_entry:
            target_rank = rank_entry.rank
    except Exception:
        pass

    if target_rank is None:
        # Fallback: compute rank on the fly
        from django.db.models import Window, F
        from django.db.models.functions import RowNumber
        # Simpler fallback: count players with higher best score
        player_best = LeaderboardEntry.objects.filter(
            player_id=player, verified=True, flagged=False
        ).aggregate(best=Max("score"))["best"]
        if player_best is None:
            from ninja.responses import Response
            return Response({"error": "Player has no verified scores."}, status=404)
        target_rank = LeaderboardEntry.objects.filter(
            verified=True, flagged=False, score__gt=player_best
        ).values("player").distinct().count() + 1

    low = max(1, target_rank - radius)
    high = target_rank + radius

    try:
        entries = LeaderboardRank.objects.filter(rank__gte=low, rank__lte=high)
    except Exception:
        entries = []

    return {
        "target_player_id": player,
        "target_rank": target_rank,
        "entries": [
            {
                "rank": e.rank,
                "player_id": e.player_id,
                "player_name": e.player_name,
                "best_score": e.best_score,
                "total_runs": e.total_runs,
                "avg_score": float(e.avg_score),
                "last_played": e.last_played,
            }
            for e in entries
        ],
    }


@router.post("/leaderboard/submit", response=LeaderboardSubmitResponseSchema, tags=["Leaderboard v2"], auth=jwt_auth)
def submit_leaderboard_entry(request, payload: LeaderboardSubmitSchema):
    """Submit a new run to the persistent leaderboard (auth required, anti-cheat enforced).

    Anti-cheat checks:
    1. Rate limiting (1 submission per 10s per player/IP).
    2. Server-side score validation (max possible score from enemy count + bonuses).
    3. Replay hash verification (non-empty, well-formed hash required).
    4. Flagged scores are hidden from global leaderboard until manual review.
    """
    from ninja.responses import Response

    user = request.auth
    try:
        player = Player.objects.get(user=user)
    except Player.DoesNotExist:
        return Response({"error": "Player profile not found."}, status=404)

    ip = _get_client_ip(request)
    ip_hash = _hash_ip(ip)

    # 1. Rate limiting
    allowed, reason = _check_rate_limit(player, ip_hash)
    if not allowed:
        ScoreSubmissionLog.objects.create(
            player=player, ip_hash=ip_hash, score=payload.score,
            accepted=False, rejection_reason=reason
        )
        return Response({
            "success": False,
            "message": reason,
            "flagged": False,
        }, status=429)

    # 2. Score validation
    valid, reason = _validate_max_possible_score(
        score=payload.score,
        enemies_killed=payload.enemies_killed,
        level_id=payload.level_id,
        powerups_used=payload.powerups_used,
        bullets_fired=payload.bullets_fired,
    )
    if not valid:
        ScoreSubmissionLog.objects.create(
            player=player, ip_hash=ip_hash, score=payload.score,
            accepted=False, rejection_reason=reason
        )
        return Response({
            "success": False,
            "message": reason,
            "flagged": True,
        }, status=400)

    # 3. Replay hash verification
    replay_ok = _verify_replay_hash(
        payload.replay_hash, payload.score, payload.enemies_killed,
        payload.duration_sec, payload.level_id
    )
    flagged = not replay_ok

    # 4. Create entry
    world = None
    if payload.world_id:
        world = World.objects.filter(id=payload.world_id).first()

    entry = LeaderboardEntry.objects.create(
        player=player,
        player_name=player.username,
        score=payload.score,
        world=world,
        level_id=payload.level_id,
        character_used=payload.character_used,
        duration_sec=payload.duration_sec,
        accuracy_pct=payload.accuracy_pct,
        enemies_killed=payload.enemies_killed,
        powerups_used=payload.powerups_used,
        replay_hash=payload.replay_hash,
        verified=replay_ok,
        flagged=flagged,
    )

    # Log submission
    ScoreSubmissionLog.objects.create(
        player=player, ip_hash=ip_hash, score=payload.score,
        accepted=True, rejection_reason=""
    )

    # Refresh materialized view asynchronously (in production, use a Celery task)
    try:
        _refresh_leaderboard_ranks()
    except Exception:
        pass

    # Compute new rank
    new_rank = LeaderboardEntry.objects.filter(
        verified=True, flagged=False, score__gt=entry.score
    ).values("player").distinct().count() + 1

    return {
        "success": True,
        "entry_id": str(entry.id),
        "is_pb": entry.is_pb,
        "new_rank": new_rank,
        "message": "Score submitted successfully." + (" Awaiting manual review." if flagged else ""),
        "flagged": flagged,
    }


# Stats endpoint (public - no auth required)
@router.get("/stats", tags=["Stats"])
def get_stats(request):
    """Get overall game statistics (public access)"""
    from django.db.models import Sum, Avg, Max
    
    total_players = Player.objects.count()
    total_sessions = GameSession.objects.count()
    total_score = Player.objects.aggregate(Sum("total_score"))["total_score__sum"] or 0
    avg_score = GameSession.objects.aggregate(Avg("score"))["score__avg"] or 0
    highest_score = GameSession.objects.aggregate(Max("score"))["score__max"] or 0
    
    return {
        "total_players": total_players,
        "total_sessions": total_sessions,
        "total_score": total_score,
        "average_score": round(avg_score, 2),
        "highest_score": highest_score,
    }


# World endpoints (public - viewing available game worlds)
@router.get("/worlds", response=List[WorldSchema], tags=["Worlds"])
def list_worlds(request):
    """Get all available game worlds/themes (public access)"""
    from .models import World
    from .schemas import WorldSchema
    return World.objects.all()


@router.get("/worlds/{world_id}", response=WorldSchema, tags=["Worlds"])
def get_world(request, world_id: int):
    """Get a specific world by ID (public access)"""
    from .models import World
    return get_object_or_404(World, id=world_id)


# Achievement endpoints (public viewing, protected for player achievements)
@router.get("/achievements", response=List[AchievementSchema], tags=["Achievements"])
def list_achievements(request):
    """Get all available achievements (public access)"""
    from .models import Achievement
    from .schemas import AchievementSchema
    return Achievement.objects.all()


@router.get("/achievements/{achievement_id}", response=AchievementSchema, tags=["Achievements"])
def get_achievement(request, achievement_id: int):
    """Get a specific achievement by ID (public access)"""
    from .models import Achievement
    return get_object_or_404(Achievement, id=achievement_id)


@router.get("/players/{player_id}/achievements", response=List[PlayerAchievementSchema], tags=["Achievements"], auth=jwt_auth)
def get_player_achievements(request, player_id: int):
    """Get all achievements for a specific player (requires authentication)"""
    from .models import PlayerAchievement
    from .schemas import PlayerAchievementSchema
    player = get_object_or_404(Player, id=player_id)
    achievements = PlayerAchievement.objects.filter(player=player).select_related('achievement')
    
    # Convert to schema format
    result = []
    for pa in achievements:
        result.append({
            "id": pa.id,
            "achievement": {
                "id": pa.achievement.id,
                "name": pa.achievement.name,
                "description": pa.achievement.description,
                "icon": pa.achievement.icon,
                "points": pa.achievement.points,
                "rarity": pa.achievement.rarity,
                "requirement_type": pa.achievement.requirement_type,
                "requirement_value": pa.achievement.requirement_value,
            },
            "earned_at": pa.earned_at,
            "unlocked_at": pa.unlocked_at,
        })
    return result


# Enhanced Profile endpoints
@router.get("/profile/me", response=EnhancedProfileSchema, tags=["Profile"], auth=jwt_auth)
def get_my_profile(request):
    """Get enhanced profile for current authenticated user"""
    from .models import Player, PlayerAchievement
    from .schemas import EnhancedProfileSchema
    
    user = request.auth
    player = get_object_or_404(Player, user=user)
    
    # Get recent achievements (last 5)
    recent_achievements = PlayerAchievement.objects.filter(
        player=player
    ).select_related('achievement').order_by('-unlocked_at')[:5]
    
    recent_list = [
        {
            "id": pa.achievement.id,
            "name": pa.achievement.name,
            "icon": pa.achievement.icon,
            "points": pa.achievement.points,
            "rarity": pa.achievement.rarity,
            "unlocked_at": pa.unlocked_at.isoformat() if pa.unlocked_at else None,
        }
        for pa in recent_achievements
    ]
    
    # Build avatar URL
    avatar_url = None
    if player.avatar:
        avatar_url = request.build_absolute_uri(player.avatar.url)
    
    return {
        "id": player.id,
        "username": player.username,
        "email": player.email or "",
        "total_score": player.total_score,
        "games_played": player.games_played,
        "highest_level": player.highest_level,
        "avatar_url": avatar_url,
        "bio": player.bio or "",
        "bg_color": player.bg_color or "#000000",
        "show_scores": player.show_scores,
        "created_at": player.created_at,
        "updated_at": player.updated_at,
        "achievements_count": PlayerAchievement.objects.filter(player=player).count(),
        "recent_achievements": recent_list,
    }


@router.patch("/profile/me", response=EnhancedProfileSchema, tags=["Profile"], auth=jwt_auth)
def update_my_profile(request, payload: ProfileUpdateSchema):
    """Update current user's profile (requires authentication)"""
    from .models import Player, PlayerAchievement
    
    user = request.auth
    player = get_object_or_404(Player, user=user)
    
    # Update only provided fields
    if payload.username is not None:
        player.username = payload.username
        user.username = payload.username
        user.save()
    
    if payload.email is not None:
        player.email = payload.email
        user.email = payload.email
        user.save()
    
    if payload.bio is not None:
        import re
        # Strip HTML tags to prevent XSS
        player.bio = re.sub(r'<[^>]+>', '', payload.bio)
    
    if payload.bg_color is not None:
        player.bg_color = payload.bg_color
    
    if payload.show_scores is not None:
        player.show_scores = payload.show_scores
    
    player.save()
    
    # Return full profile (same as GET /profile/me)
    avatar_url = None
    if player.avatar:
        avatar_url = request.build_absolute_uri(player.avatar.url)
    
    recent_achievements = PlayerAchievement.objects.filter(
        player=player
    ).select_related('achievement').order_by('-unlocked_at')[:5]
    
    recent_list = [
        {
            "id": pa.achievement.id,
            "name": pa.achievement.name,
            "icon": pa.achievement.icon,
            "points": pa.achievement.points,
            "rarity": pa.achievement.rarity,
            "unlocked_at": pa.unlocked_at.isoformat() if pa.unlocked_at else None,
        }
        for pa in recent_achievements
    ]
    
    return {
        "id": player.id,
        "username": player.username,
        "email": player.email or "",
        "total_score": player.total_score,
        "games_played": player.games_played,
        "highest_level": player.highest_level,
        "avatar_url": avatar_url,
        "bio": player.bio or "",
        "bg_color": player.bg_color or "#000000",
        "show_scores": player.show_scores,
        "created_at": player.created_at,
        "updated_at": player.updated_at,
        "achievements_count": PlayerAchievement.objects.filter(player=player).count(),
        "recent_achievements": recent_list,
    }


@router.post("/profile/me/avatar", tags=["Profile"], auth=jwt_auth)
def upload_avatar(request):
    """Upload avatar image for current user (max 5MB, PNG/JPG/GIF)"""
    from django.core.files.uploadhandler import MemoryFileUploadHandler
    
    user = request.auth
    player = get_object_or_404(Player, user=user)
    
    avatar_file = request.FILES.get('avatar')
    if not avatar_file:
        from ninja.responses import Response
        return Response({"error": "No avatar file provided"}, status=400)

    # Reject empty files
    if avatar_file.size == 0:
        from ninja.responses import Response
        return Response({"error": "File is empty."}, status=400)

    # Validate file size (5MB)
    if avatar_file.size > 5 * 1024 * 1024:
        from ninja.responses import Response
        return Response({"error": "File too large. Maximum 5MB."}, status=400)

    # Validate file type by content_type header
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if avatar_file.content_type not in allowed_types:
        from ninja.responses import Response
        return Response({"error": "Invalid file type. Use PNG, JPG, GIF or WebP."}, status=400)

    # Magic-byte validation — catches files with a mismatched extension / content-type
    MAGIC_BYTES = {
        'image/png':  b'\x89PNG',
        'image/jpeg': b'\xff\xd8\xff',
        'image/gif':  b'GIF8',
        'image/webp': b'RIFF',
    }
    if avatar_file.content_type in MAGIC_BYTES:
        header = avatar_file.read(8)
        avatar_file.seek(0)
        if not header.startswith(MAGIC_BYTES[avatar_file.content_type]):
            from ninja.responses import Response
            return Response(
                {"error": "File content does not match its declared type."},
                status=400,
            )
    
    # Delete old avatar if exists
    if player.avatar:
        player.avatar.delete(save=False)
    
    # Save new avatar
    player.avatar = avatar_file
    player.save()
    
    avatar_url = request.build_absolute_uri(player.avatar.url)
    return {"message": "Avatar uploaded successfully", "avatar_url": avatar_url}


# ── Boot Camp / Tutorial endpoints ─────────────────────────────────────

@router.get("/bootcamp/status", response=BootCampStatusSchema, tags=["Boot Camp"], auth=jwt_auth)
def get_bootcamp_status(request):
    """Get Boot Camp completion status for current user"""
    from .models import Player, PlayerAchievement
    
    user = request.auth
    player = get_object_or_404(Player, user=user)
    
    # Check for Graduate achievement
    has_graduate_badge = PlayerAchievement.objects.filter(
        player=player,
        achievement__name="Boot Camp Graduate"
    ).exists()
    
    # Determine unlocked worlds
    worlds_unlocked = ["BootCamp"]
    if player.boot_camp_completed:
        worlds_unlocked.append("Space")
    
    return {
        "boot_camp_completed": player.boot_camp_completed,
        "graduate_badge": has_graduate_badge,
        "worlds_unlocked": worlds_unlocked,
    }


@router.post("/bootcamp/complete", response=BootCampCompleteSchema, tags=["Boot Camp"], auth=jwt_auth)
def complete_bootcamp(request):
    """Mark Boot Camp as completed - unlocks Space world and awards Graduate badge"""
    from .models import Player, Achievement, PlayerAchievement
    
    user = request.auth
    player = get_object_or_404(Player, user=user)
    
    # Mark Boot Camp as completed
    player.boot_camp_completed = True
    player.save()
    
    # Create or get the Graduate achievement
    graduate_achievement, created = Achievement.objects.get_or_create(
        name="Boot Camp Graduate",
        defaults={
            "description": "Complete the Boot Camp tutorial to begin your journey",
            "icon": "🎓",
            "points": 50,
            "rarity": "COMMON",
            "achievement_type": "GRADUATE",
            "requirement_type": "bootcamp_complete",
            "requirement_value": 1,
        }
    )
    
    # Award the achievement if not already earned
    player_achievement, pa_created = PlayerAchievement.objects.get_or_create(
        player=player,
        achievement=graduate_achievement,
    )
    
    return {
        "message": "Boot Camp completed! Space world unlocked.",
        "graduate_badge": True,
        "space_unlocked": True,
    }


@router.get("/bootcamp/progress", response=TutorialProgressSchema, tags=["Boot Camp"], auth=jwt_auth)
def get_tutorial_progress(request):
    """Get current tutorial progress for the user"""
    from .models import Player, GameSession
    
    user = request.auth
    player = get_object_or_404(Player, user=user)
    
    # Get the most recent tutorial session
    latest_tutorial = GameSession.objects.filter(
        player=player,
        is_tutorial=True
    ).order_by('-started_at').first()
    
    if latest_tutorial:
        return {
            "objectives_completed": latest_tutorial.tutorial_objectives_completed,
            "total_objectives": 5,
            "current_objective": None,
            "completed": latest_tutorial.completed,
        }
    
    return {
        "objectives_completed": 0,
        "total_objectives": 5,
        "current_objective": None,
        "completed": False,
    }


@router.post("/bootcamp/progress", response=TutorialProgressSchema, tags=["Boot Camp"], auth=jwt_auth)
def update_tutorial_progress(request, objectives_completed: int):
    """Update tutorial progress - called during gameplay"""
    from .models import Player, GameSession
    
    user = request.auth
    player = get_object_or_404(Player, user=user)
    
    # Get or create the tutorial session
    session, created = GameSession.objects.get_or_create(
        player=player,
        is_tutorial=True,
        completed=False,
        defaults={
            "score": 0,
            "level_reached": 1,
            "enemies_killed": 0,
            "duration_seconds": 0,
        }
    )
    
    session.tutorial_objectives_completed = objectives_completed
    if objectives_completed >= 5:
        session.completed = True
        session.ended_at = timezone.now()
    session.save()
    
    return {
        "objectives_completed": session.tutorial_objectives_completed,
        "total_objectives": 5,
        "current_objective": None,
        "completed": session.completed,
    }
