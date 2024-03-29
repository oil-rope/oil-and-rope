# Generated by Django 4.0.4 on 2022-06-26 12:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('roleplay', '0010_transform_user_null_to_public'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='user',
        ),
        migrations.AlterField(
            model_name='place',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='place_set', to=settings.AUTH_USER_MODEL, verbose_name='owner'),
            preserve_default=False,
        ),
    ]
