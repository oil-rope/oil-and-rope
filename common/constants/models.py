from django.conf import settings

# Auth
USER_MODEL = settings.AUTH_USER_MODEL
GROUP_MODEL = 'auth.Group'
PERMISSION_MODEL = 'auth.Permission'

# Content Types
CONTENT_TYPE_MODEL = 'contenttypes.ContentType'

# Dynamic Menu
DYNAMIC_MENU = 'dynamic_menu.DynamicMenu'

# Roleplay
DOMAIN_MODEL = 'roleplay.Domain'
PLACE_MODEL = 'roleplay.Place'
RACE_MODEL = 'roleplay.Race'
USER_RACE_RELATION = 'roleplay.RaceUser'
MUSIC_MODEL = 'roleplay.Music'
USER_MUSIC_RELATION = 'roleplay.MusicUser'
