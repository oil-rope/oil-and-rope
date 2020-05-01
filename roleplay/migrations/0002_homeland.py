# Generated by Django 2.2.12 on 2020-05-01 17:35

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import roleplay.models


class Migration(migrations.Migration):

    dependencies = [
        ('roleplay', '0001_initial_squashed_0002_domain_domain_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Homeland',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_created_at', models.DateTimeField(auto_now_add=True, verbose_name='Entry created at')),
                ('entry_updated_at', models.DateTimeField(auto_now=True, verbose_name='Entry updated at')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('site_type', models.PositiveSmallIntegerField(choices=[(0, 'House'), (1, 'Town'), (2, 'Village'), (3, 'City'), (4, 'Metropolis'), (5, 'Forest'), (6, 'Hills'), (7, 'Mountains'), (8, 'Mines'), (9, 'River'), (10, 'Sea'), (11, 'Desert'), (12, 'Tundra'), (13, 'Unusual')], default=1, verbose_name='Site type')),
                ('image', models.ImageField(blank=True, null=True, upload_to=roleplay.models.homeland_upload_to, verbose_name='Image')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent_site', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_sites', to='roleplay.Homeland', verbose_name='Parent site')),
            ],
            options={
                'verbose_name': 'Homeland',
                'verbose_name_plural': 'Homelands',
                'ordering': ['name', '-entry_created_at', '-entry_updated_at'],
            },
        ),
    ]
