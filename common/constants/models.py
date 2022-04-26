from django.conf import settings

# Auth
AUTH_GROUP = 'auth.Group'
AUTH_PERMISSION = 'auth.Permission'

# Registration
REGISTRATION_USER = settings.AUTH_USER_MODEL
REGISTRATION_PROFILE = 'registration.Profile'

# Common
COMMON_TRACK = 'common.Track'

# Bot
DISCORD_USER_MODEL = 'bot.DiscordUser'
DISCORD_SERVER_MODEL = 'bot.DiscordServer'
DISCORD_TEXT_CHANNEL_MODEL = 'bot.DiscordTextChannel'

# Content Types
CONTENT_TYPE = 'contenttypes.ContentType'

# Dynamic Menu
DYNAMIC_MENU = 'dynamic_menu.DynamicMenu'

# Roleplay
ROLEPLAY_DOMAIN = 'roleplay.Domain'
ROLEPLAY_PLACE = 'roleplay.Place'
ROLEPLAY_RACE = 'roleplay.Race'
ROLEPLAY_RACE_USER = 'roleplay.RaceUser'
ROLEPLAY_SESSION = 'roleplay.Session'
ROLEPLAY_PLAYER_IN_SESSION = 'roleplay.PlayerInSession'

# Chat
CHAT = 'chat.Chat'
CHAT_MESSAGE = 'chat.ChatMessage'
