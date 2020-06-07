# Generated by Django 2.2.12 on 2020-05-16 09:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('roleplay', '0004_auto_20200509_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='places_owned', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='place',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='places', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
