# Generated migration for character unlock tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_seed_worlds'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='unlocked_characters',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
