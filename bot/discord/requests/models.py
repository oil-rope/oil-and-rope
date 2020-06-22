from django.conf import settings

from .utils import discord_api_post, discord_api_get


class ApiMixin:
    """
    This class loads content from `response` into class attributtes.
    """

    def __init__(self, url):
        self.url = url
        self.response = discord_api_get(self.url)
        self.json_response = self.response.json()

        # Magic attributes
        for key, value in self.json_response.items():
            setattr(self, key, value)


class User(ApiMixin):
    """
    Represents a Discord User.
    """

    base_url = f'{settings.DISCORD_API_URL}users/'

    def __init__(self, id):
        self.id = id
        url = f'{self.base_url}{self.id}'
        super().__init__(url)

    def create_dm(self):
        """
        Creates a DM with this User.
        """

        url = f'{self.base_url}@me/channels'
        data = {
            'recipient_id': self.id
        }
        response = discord_api_post(url, data=data)
        json_response = response.json()

        return Channel(json_response['id'])

    def send_message(self, content):
        """
        Sends a message to this user.
        """

        dm = self.create_dm()
        response = dm.send_message(content)
        return response


class Channel(ApiMixin):
    """
    Represents a Discord Channel.
    """

    base_url = f'{settings.DISCORD_API_URL}channels/'

    def __init__(self, id):
        self.id = id
        url = f'{self.base_url}{self.id}'
        super().__init__(url)

    def send_message(self, content):
        url = f'{self.url}/messages'
        data = {
            'content': content
        }
        response = discord_api_post(url, data=data)
        return response
