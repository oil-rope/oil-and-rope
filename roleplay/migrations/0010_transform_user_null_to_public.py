# Generated by Django 4.0.4 on 2022-06-26 12:21

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.models import Model


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    # We get Place model
    Place: Model = apps.get_model('roleplay', 'Place')
    db_alias = schema_editor.connection.alias
    # We select all "public places"
    Place.objects.using(db_alias).filter(
        user__isnull=True,
        is_public=False,
    ).update(is_public=True)


def reverse_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    # We get Place model
    Place: Model = apps.get_model('roleplay', 'Place')
    db_alias = schema_editor.connection.alias
    # We select all "public places"
    Place.objects.using(db_alias).filter(
        user__isnull=True,
        is_public=True,
    ).update(is_public=False)


class Migration(migrations.Migration):
    dependencies = [
        ('roleplay', '0009_place_is_public'),
    ]

    operations = [
        migrations.RunPython(code=forwards_func, reverse_code=reverse_func)
    ]
