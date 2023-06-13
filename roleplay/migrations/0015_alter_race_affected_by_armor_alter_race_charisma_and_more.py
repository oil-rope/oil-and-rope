# Generated by Django 4.1 on 2023-02-13 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roleplay', '0014_populate_initial_trait_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='race',
            name='affected_by_armor',
            field=models.BooleanField(blank=True, default=True, help_text='declares if this race is affected by armor penalties', verbose_name='affected by armor'),
        ),
        migrations.AlterField(
            model_name='race',
            name='charisma',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='charisma'),
        ),
        migrations.AlterField(
            model_name='race',
            name='constitution',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='constitution'),
        ),
        migrations.AlterField(
            model_name='race',
            name='dexterity',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='dexterity'),
        ),
        migrations.AlterField(
            model_name='race',
            name='intelligence',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='intelligence'),
        ),
        migrations.AlterField(
            model_name='race',
            name='strength',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='strength'),
        ),
        migrations.AlterField(
            model_name='race',
            name='wisdom',
            field=models.SmallIntegerField(blank=True, default=0, verbose_name='wisdom'),
        ),
    ]