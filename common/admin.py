from django.contrib import admin

from core.admin import TracingMixinAdmin, make_private, make_public

from .models import Track, Vote


@admin.register(Track)
class TrackAdmin(TracingMixinAdmin):
    actions = [make_public, make_private]
    fields = ('name', 'description', 'owner', 'public', 'file')
    list_display = ('id', 'name', 'file', 'owner', 'public', 'entry_created_at', 'entry_updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('public', 'entry_created_at', 'entry_updated_at')
    search_fields = ['id', 'name', 'owner__username']


@admin.register(Vote)
class VoteAdmin(TracingMixinAdmin):
    autocomplete_fields = [
        'user',
    ]
    fields = (
        'user',
        'content_type',
        'object_id',
        'is_positive',
    )
    list_display = (
        '__str__',
        'id',
        'is_positive',
        'user',
        'content_object',
        'entry_created_at',
        'entry_updated_at',
    )
    list_display_links = (
        '__str__',
        'id',
    )
    search_fields = [
        'id__icontains',
    ]
