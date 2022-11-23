# Generated by Django 4.1 on 2022-11-16 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0008_create_bot_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], default='en', max_length=10, verbose_name='language'),
        ),
    ]