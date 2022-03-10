from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.admin import TracingMixinAdmin

from .models import Profile, User


@admin.register(Profile)
class ProfileAdmin(TracingMixinAdmin):
    """
    Model manager for :class:Profile.
    """

    search_fields = ('user__username', 'user__first_name')


admin.site.register(User, UserAdmin)
