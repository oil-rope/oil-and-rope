from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.admin import TracingMixinAdmin

from .models import Track


@admin.register(Track)
class TrackAdmin(TracingMixinAdmin):
    actions = ['make_public', 'make_private']
    date_hierarchy = 'entry_created_at'
    fields = ('name', 'description', 'owner', 'public', 'file')
    list_display = ('id', 'name', 'file', 'owner', 'public', 'entry_created_at', 'entry_updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('public', 'entry_created_at', 'entry_updated_at')
    search_fields = ['id', 'name', 'owner__username']

    @admin.action(description=_('mark selected tracks as public').capitalize())
    def make_public(self, request, queryset):
        queryset.update(public=True)

    @admin.action(description=_('mark selected tracks as private').capitalize())
    def make_private(self, request, queryset):
        queryset.update(public=False)
