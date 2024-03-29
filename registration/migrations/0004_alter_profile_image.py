# Generated by Django 4.0.3 on 2022-03-07 12:00

import common.files.upload
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_alter_profile_alias_alter_profile_web'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to=common.files.upload.default_upload_to, verbose_name='avatar'),
            preserve_default=False,
        ),
    ]
