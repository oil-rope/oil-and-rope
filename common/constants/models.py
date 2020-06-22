from django.conf import settings

# Auth
USER_MODEL = settings.AUTH_USER_MODEL

# Roleplay
DOMAIN_MODEL = 'roleplay.Domain'
PLACE_MODEL = 'roleplay.Place'
RACE_MODEL = 'roleplay.Race'
USER_RACE_RELATION = 'roleplay.RaceUser'