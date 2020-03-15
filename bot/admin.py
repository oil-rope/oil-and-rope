from django.contrib import admin

from core.admin import TracingMixinAdmin

from .models import DiscordServer, DiscordTextChannel, DiscordUser, DiscordVoiceChannel


@admin.register(DiscordUser)
class DiscordUserAdmin(TracingMixinAdmin):
    """
    Manager for :class:`DiscordUser`.
    """

    search_fields = ('nick', 'code')
    list_filter = ('premium', )


@admin.register(DiscordServer)
class DiscordServerAdmin(TracingMixinAdmin):
    """
    Manager for :class:`DiscordServer`.
    """

    search_fields = ('name', 'owner__nick')
    list_filter = ('region', )


@admin.register(DiscordTextChannel)
class DiscordTextChannelAdmin(TracingMixinAdmin):
    """
    Manager for :class:`DiscordTextChannel`.
    """

    search_fields = ('name', )
    list_filter = ('nsfw', 'news')


@admin.register(DiscordVoiceChannel)
class DiscordVoiceChannelAdmin(admin.ModelAdmin):
    """
    Manager for :class:`DiscordVoiceChannel`.
    """

    search_fields = ('name', )
