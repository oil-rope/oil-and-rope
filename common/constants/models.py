from django.conf import settings

# Auth
USER_MODEL = settings.AUTH_USER_MODEL
GROUP_MODEL = 'auth.Group'
PERMISSION_MODEL = 'auth.Permission'

# Registration
PROFILE_MODEL = 'registration.Profile'

# Bot
DISCORD_USER_MODEL = 'bot.DiscordUser'
DISCORD_SERVER_MODEL = 'bot.DiscordServer'
DISCORD_TEXT_CHANNEL_MODEL = 'bot.DiscordTextChannel'

# Content Types
CONTENT_TYPE_MODEL = 'contenttypes.ContentType'

# Dynamic Menu
DYNAMIC_MENU = 'dynamic_menu.DynamicMenu'

# Roleplay
DOMAIN_MODEL = 'roleplay.Domain'
PLACE_MODEL = 'roleplay.Place'
RACE_MODEL = 'roleplay.Race'
USER_RACE_RELATION = 'roleplay.RaceUser'
SESSION_MODEL = 'roleplay.Session'

# Chat
CHAT_MODEL = 'chat.Chat'
CHAT_MESSAGE_MODEL = 'chat.ChatMessage'
