# Generated by Django 3.0.8 on 2020-09-19 11:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0003_auto_20200918_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_message_set', to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_message_set', to='chat.Chat', verbose_name='Chat'),
        ),
    ]
