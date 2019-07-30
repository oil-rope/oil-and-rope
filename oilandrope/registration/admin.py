from django.contrib import admin

from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Model manager for :class:Profile.
    """

    readonly_fields = ('created_at', 'updated_at')
