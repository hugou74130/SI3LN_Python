"""
Add game_world_id to LeaderboardEntry.

Stores the game-side integer world ID (0=BootCamp, 1=Space, 2=Desert, …)
directly, decoupled from the World FK whose PK sequence doesn't cover 0.
Existing rows are back-filled from the FK value so historical data is preserved.
"""
from django.db import migrations, models


def populate_game_world_id(apps, schema_editor):
    LeaderboardEntry = apps.get_model("game", "LeaderboardEntry")
    for entry in LeaderboardEntry.objects.filter(world_id__isnull=False):
        entry.game_world_id = entry.world_id
        entry.save(update_fields=["game_world_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0005_player_unlocked_characters"),
    ]

    operations = [
        migrations.AddField(
            model_name="leaderboardentry",
            name="game_world_id",
            field=models.IntegerField(
                blank=True,
                null=True,
                db_index=True,
                help_text="Game-side world ID (0=BootCamp, 1=Space, …)",
            ),
        ),
        migrations.AddIndex(
            model_name="leaderboardentry",
            index=models.Index(fields=["game_world_id", "-score"], name="game_leaderb_game_wo_idx"),
        ),
        migrations.RunPython(populate_game_world_id, reverse_code=migrations.RunPython.noop),
    ]
