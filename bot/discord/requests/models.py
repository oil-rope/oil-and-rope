from .utils import discord_api_request

DISCORD_API_URL = 'https://discord.com/api'


class User:

    def __init__(self, id):
        self.id = id
        self.url = f'{DISCORD_API_URL}/users/{self.id}'
        self.response = discord_api_request(self.url)
