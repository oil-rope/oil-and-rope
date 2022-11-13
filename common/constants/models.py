from django.conf import settings

# Auth
AUTH_GROUP = 'auth.Group'
AUTH_PERMISSION = 'auth.Permission'

# Registration
REGISTRATION_USER = settings.AUTH_USER_MODEL
REGISTRATION_PROFILE = 'registration.Profile'

# Common
COMMON_TRACK = 'common.Track'
COMMON_IMAGE = 'common.Image'
COMMON_VOTE = 'common.Vote'

# Bot
DISCORD_USER_MODEL = 'bot.DiscordUser'
DISCORD_SERVER_MODEL = 'bot.DiscordServer'
DISCORD_TEXT_CHANNEL_MODEL = 'bot.DiscordTextChannel'

# Content Types
CONTENT_TYPE = 'contenttypes.ContentType'

# Roleplay
ROLEPLAY_CAMPAIGN = 'roleplay.Campaign'
ROLEPLAY_PLAYER_IN_CAMPAIGN = 'roleplay.PlayerInCampaign'
ROLEPLAY_DOMAIN = 'roleplay.Domain'
ROLEPLAY_PLACE = 'roleplay.Place'
ROLEPLAY_RACE = 'roleplay.Race'
ROLEPLAY_RACE_USER = 'roleplay.RaceUser'
ROLEPLAY_SESSION = 'roleplay.Session'

# Chat
CHAT = 'chat.Chat'
CHAT_MESSAGE = 'chat.ChatMessage'
