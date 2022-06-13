from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from core.admin import make_private, make_public

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


class PlayerInCampaignInline(admin.TabularInline):
    model = models.PlayerInCampaign
    extra = 1


@admin.register(models.Campaign)
class CampaignAdmin(admin.ModelAdmin):
    date_hierarchy = 'entry_created_at'
    inlines = [PlayerInCampaignInline]
    fields = (
        ('name', 'summary', 'system', 'place', 'owner'),
        'description',
        ('start_date', 'end_date'),
        'discord_channel_id',
        'cover_image',
        'is_public',
    )
    list_display = (
        '__str__',
        'id',
        'name',
        'system',
        'owner',
        'is_public',
        'place',
        'start_date',
        'end_date',
        'chat',
        'entry_created_at',
        'entry_updated_at',
    )
    list_display_links = ('__str__', 'id', 'name')
    list_filter = (
        'system',
        'is_public',
        'start_date',
        'end_date',
        'entry_created_at',
        'entry_updated_at',
    )
    readonly_fields = ('entry_created_at', 'entry_updated_at')
    search_fields = ['name__icontains', 'owner__username__icontains']
    actions = [make_public, make_private]

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.chat.delete()
        queryset.delete()


class RaceInline(admin.TabularInline):
    model = models.RaceUser


@admin.register(models.Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
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
        'entry_created_at',
        'entry_updated_at',
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


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    date_hierarchy = 'entry_created_at'
    fields = (
        'name',
        'plot',
        'description',
        'next_game',
        'image',
        'campaign',
    )
    list_display = (
        '__str__',
        'id',
        'name',
        'next_game',
        'entry_created_at',
        'entry_updated_at',
    )
    list_display_links = ('__str__', 'id', 'name',)
    list_filter = ('next_game', 'entry_created_at', 'entry_updated_at')
    readonly_fields = ('entry_created_at', 'entry_updated_at')
    search_fields = ['name__icontains', 'campaign__place__name__icontains']
