# Generated by Django 4.0.3 on 2022-03-30 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0006_user_discord_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
    ]
