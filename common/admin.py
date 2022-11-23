from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from core.admin import TracingMixinAdmin, make_private, make_public

from . import models


@admin.register(models.Track)
class TrackAdmin(TracingMixinAdmin):
    actions = [make_public, make_private]
    fields = ('name', 'description', 'owner', 'public', 'file')
    list_display = ('id', 'name', 'file', 'owner', 'public', 'entry_created_at', 'entry_updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('public', 'entry_created_at', 'entry_updated_at')
    search_fields = ['id', 'name', 'owner__username']


class ImageTabularInline(GenericTabularInline):
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 1
    model = models.Image


@admin.register(models.Vote)
class VoteAdmin(TracingMixinAdmin):
    actions = ['make_positive', 'make_negative']
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
        'user__username__icontains',
    ]

    @admin.action(description=_('Mark selected votes as positive'))
    def make_positive(self, request, queryset):
        updated = queryset.update(is_positive=True)
        self.message_user(request, ngettext(
            '%d vote was successfully marked as positive.',
            '%d votes were successfully marked as positive.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description=_('Mark selected votes as negative'))
    def make_negative(self, request, queryset):
        updated = queryset.update(is_positive=False)
        self.message_user(request, ngettext(
            '%d vote was successfully marked as negative.',
            '%d votes were successfully marked as negative.',
            updated,
        ) % updated, messages.SUCCESS)
