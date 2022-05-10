from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from mptt.admin import DraggableMPTTAdmin

from . import models


@admin.action(description=_('Mark selected campaigns as public'), permissions=['change'])
def make_public(modeladmin, request, queryset):
    updated = queryset.update(is_public=True)
    modeladmin.message_user(request, ngettext(
        '%d instance was successfully marked as public.',
        '%d instances were successfully marked as public.',
        updated,
    ) % updated, messages.SUCCESS)


@admin.action(description=_('Mark selected campaigns as private'), permissions=['change'])
def make_private(modeladmin, request, queryset):
    updated = queryset.update(is_public=False)
    modeladmin.message_user(request, ngettext(
        '%d instance was successfully marked as private.',
        '%d instances were successfully marked as private.',
        updated,
    ) % updated, messages.SUCCESS)


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
        ('name', 'resume', 'system', 'place', 'owner'),
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


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    date_hierarchy = 'entry_created_at'
    fields = (
        ('name', 'system'),
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
        'system',
        'next_game',
        'entry_created_at',
        'entry_updated_at',
    )
    list_display_links = ('__str__', 'id', 'name',)
    list_filter = ('system', )
    readonly_fields = ('entry_created_at', 'entry_updated_at')
    search_fields = ['name__icontains', 'world__name__icontains']
