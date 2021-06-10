# Generated by Django 3.1.1 on 2020-09-29 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bot', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='discorduser',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discord_user', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='discordtextchannel',
            name='discord_users',
            field=models.ManyToManyField(related_name='discord_text_channels', to='bot.DiscordUser', verbose_name='Discord Users'),
        ),
        migrations.AddField(
            model_name='discordtextchannel',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discord_text_channels', to='bot.discordserver', verbose_name='Discord Server'),
        ),
        migrations.AddField(
            model_name='discordserver',
            name='discord_users',
            field=models.ManyToManyField(related_name='discord_servers', to='bot.DiscordUser', verbose_name='Discord Users'),
        ),
        migrations.AddField(
            model_name='discordserver',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_servers', to='bot.discorduser', verbose_name='Owner'),
        ),
    ]