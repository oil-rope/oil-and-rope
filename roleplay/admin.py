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


class PlayersInSessionInline(admin.TabularInline):
    model = models.PlayerInSession
    extra = 1


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    date_hierarchy = 'entry_created_at'
    inlines = (PlayersInSessionInline, )
    fields = (('name', 'system'), 'plot', 'next_game', 'chat', 'world')
    filter_horizontal = ('players', )
    list_display = ('__str__', 'id', 'system', 'next_game', 'entry_created_at', 'entry_updated_at')
    list_display_links = ('__str__', 'id')
    list_filter = ('system', )
    readonly_fields = ('entry_created_at', 'entry_updated_at')
    search_fields = ['name__icontains', 'world__name__icontains']

    def delete_model(self, request, obj):
        obj.chat.delete()
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.chat.delete()
        queryset.delete()
