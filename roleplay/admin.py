from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from . import models


@admin.register(models.Domain)
class DomainAdmin(admin.ModelAdmin):
    date_hierarchy = 'entry_created_at'
    list_display = ('__str__', 'domain_type', 'entry_created_at', 'entry_updated_at')
    list_display_links = ('__str__',)
    list_filter = ('domain_type',)
    readonly_fields = ('entry_created_at', 'entry_updated_at')
    search_fields = ['name__icontains']


@admin.register(models.Place)
class PlaceAdmin(DraggableMPTTAdmin):
    date_hierarchy = 'entry_created_at'
    list_display = ('tree_actions', 'indented_title', '__str__', 'site_type', 'entry_created_at', 'entry_updated_at')
    list_display_links = ('indented_title', '__str__')
    list_filter = ('site_type',)
    readonly_fields = ('entry_created_at', 'entry_updated_at')
    search_fields = ['name__icontains']


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    date_hierarchy = 'entry_created_at'
    fields = (('name', 'system'), 'next_game')
    list_display = ('__str__', 'system', 'next_game', 'entry_created_at')
    list_display_links = ('__str__', )
    list_filter = ('system', )
    readonly_fields = ('entry_created_at', 'entry_updated_at')


class RaceInline(admin.TabularInline):
    model = models.RaceUser 


@admin.register(models.Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'entry_created_at',
        'entry_updated_at',
        'name',
        'description',
        'strength',
        'dexterity',
        'constitution',
        'intelligence',
        'wisdom',
        'charisma',
        'affected_by_armor',
        'image',
    )

    inlines = [
        RaceInline
    ]

    list_filter = (
        'entry_created_at',
        'entry_updated_at',
        'affected_by_armor',
    )
    raw_id_fields = ('users',)
    search_fields = ('name',)


@admin.register(models.RaceUser)
class RaceUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'entry_created_at',
        'entry_updated_at',
        'user',
        'race',
        'is_owner',
    )
    list_filter = (
        'entry_created_at',
        'entry_updated_at',
        'user',
        'race',
        'is_owner',
    )
