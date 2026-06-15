# Generated manually for Issue #3 — Persistent Leaderboard Database

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ('game', '0004_leaderboard_models'),
    ]

    operations = [
        # LeaderboardEntry already exists in the codebase (added in a prior migration)
        # This migration ensures the materialized view leaderboard_ranks is created
        migrations.RunSQL(
            sql="""
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
            """,
            reverse_sql="DROP TABLE IF EXISTS leaderboard_ranks;"
        ),
    ]
