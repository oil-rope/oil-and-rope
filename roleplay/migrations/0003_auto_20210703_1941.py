# Generated by Django 3.2.5 on 2021-07-03 18:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('roleplay', '0002_auto_20210701_1633'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='playerinsession',
            options={'verbose_name': 'player in session', 'verbose_name_plural': 'players in sessions'},
        ),
        migrations.AlterField(
            model_name='session',
            name='system',
            field=models.PositiveSmallIntegerField(choices=[(0, 'pathfinder'), (1, 'dungeons & dragons')], verbose_name='system'),
        ),
        migrations.AlterUniqueTogether(
            name='playerinsession',
            unique_together={('session', 'player')},
        ),
    ]