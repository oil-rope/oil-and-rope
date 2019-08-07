from django.contrib import admin

from core.admin import TracingMixinAdmin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(TracingMixinAdmin):
    """
    Model manager for :class:Profile.
    """

    search_fields = ('user__username', 'user__first_name', 'alias')
