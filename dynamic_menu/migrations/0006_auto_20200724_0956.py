# Generated by Django 3.0.8 on 2020-07-24 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dynamic_menu', '0005_auto_20200722_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dynamicmenu',
            name='related_models',
            field=models.ManyToManyField(blank=True, related_name='menus', to='contenttypes.ContentType', verbose_name='Related Models'),
        ),
    ]
