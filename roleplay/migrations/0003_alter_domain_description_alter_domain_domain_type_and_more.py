# Generated by Django 4.0.2 on 2022-02-21 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roleplay', '0002_alter_domain_entry_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='domain',
            name='domain_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Domain'), (1, 'Subdomain')], default=0, verbose_name='domain type'),
        ),
        migrations.AlterField(
            model_name='place',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='place',
            name='site_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'House'), (1, 'Town'), (2, 'Village'), (3, 'City'), (4, 'Metropolis'), (5, 'Forest'), (6, 'Hills'), (7, 'Mountains'), (8, 'Mines'), (9, 'River'), (10, 'Sea'), (11, 'Desert'), (12, 'Tundra'), (13, 'Unusual'), (14, 'Island'), (15, 'Country'), (16, 'Continent'), (17, 'World'), (18, 'Ocean')], default=1, verbose_name='site type'),
        ),
        migrations.AlterField(
            model_name='race',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='session',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
            preserve_default=False,
        ),
    ]