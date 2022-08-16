from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext


@admin.action(description=_('Mark selected as public'), permissions=['change'])
def make_public(modeladmin, request, queryset):
    updated = queryset.update(is_public=True)
    modeladmin.message_user(request, ngettext(
        '%d instance was successfully marked as public.',
        '%d instances were successfully marked as public.',
        updated,
    ) % updated, messages.SUCCESS)


@admin.action(description=_('Mark selected as private'), permissions=['change'])
def make_private(modeladmin, request, queryset):
    updated = queryset.update(is_public=False)
    modeladmin.message_user(request, ngettext(
        '%d instance was successfully marked as private.',
        '%d instances were successfully marked as private.',
        updated,
    ) % updated, messages.SUCCESS)


class TracingMixinAdmin(admin.ModelAdmin):
    """
    Manager for tracing features.
    """

    date_hierarchy = 'entry_created_at'
    readonly_fields = ('entry_created_at', 'entry_updated_at')
    list_filter = ('entry_created_at', 'entry_updated_at')
