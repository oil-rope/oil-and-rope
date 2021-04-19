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


@admin.register(models.Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'entry_created_at',
        'entry_updated_at',
        'title',
        'description',
        'file',
        'content_type',
        'object_id',
    )
    list_filter = ('entry_created_at', 'entry_updated_at', 'content_type')
    readonly_fields = ('entry_created_at', 'entry_updated_at')
    search_fields = ['tile__icontains']
