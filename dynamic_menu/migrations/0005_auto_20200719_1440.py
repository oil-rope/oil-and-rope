# Generated by Django 3.0.8 on 2020-07-19 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_menu', '0004_auto_20200429_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dynamicmenu',
            name='menu_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Standard menu'), (1, 'Context menu')], default=0, verbose_name='Menu Type'),
        ),
    ]
