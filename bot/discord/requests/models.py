from django.conf import settings

from .enums import ChannelTypes, MessageTypes
from .utils import discord_api_get, discord_api_post
from bot.exceptions import HelpfulError


class ApiMixin:
    """
    This class loads content from `response` into class attributtes.
    """

    def __init__(self, url=None, *, response=None):
        self.url = self.get_url(url)

        if not self.url:
            raise HelpfulError('URL canno be None.', 'Please declare a url or overwrite `get_url` method.')

        if response:
            self.response = response
        else:
            self.response = discord_api_get(self.url)
        self.json_response = self.response.json()

        # Magic attributes
        for key, value in self.json_response.items():
            setattr(self, key, value)

    def get_url(self, url=None):
        return url


class User(ApiMixin):
    """
    Represents a Discord User.
    """

    base_url = f'{settings.DISCORD_API_URL}users/'

    def __init__(self, id, *, response=None):
        self.id = id
        super().__init__(self.get_url(), response=response)

    @classmethod
    def from_bot(cls):
        url = f'{cls.base_url}@me'
        response = discord_api_get(url)
        response_json = response.json()
        return cls(response_json['id'], response=response)

    def get_url(self, url=None):
        return f'{self.base_url}{self.id}'

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
        channel_id = json_response['id']

        # Creating object from response should be faster
        return Channel(channel_id, response=response)

    def send_message(self, content):
        """
        Sends a message to this user.
        """

        dm = self.create_dm()
        response = dm.send_message(content)
        return response

    def __str__(self):
        return f'{self.username} ({self.id})'

    def __repr__(self):
        return self.__str__()


class Channel(ApiMixin):
    """
    Represents a Discord Channel.
    """

    base_url = f'{settings.DISCORD_API_URL}channels/'

    def __init__(self, id, *, response=None):
        self.id = id
        super().__init__(self.get_url(), response=response)
        self.type = ChannelTypes(self.type)

    def get_url(self, url=None):
        return f'{self.base_url}{self.id}'

    def send_message(self, content):
        url = f'{self.url}/messages'
        data = {
            'content': content
        }
        response = discord_api_post(url, data=data)
        msg_id = response.json()['id']

        # Creating message from given response should be faster
        msg = Message(self, msg_id, response=response)
        return msg

    def __str__(self):
        if hasattr(self, 'name'):
            return f'Channel {self.name} ({self.id})'
        return f'Channel {self.type.name} ({self.id})'

    def __repr__(self):
        return self.__str__()


class Message(ApiMixin):
    """
    Represents a Discord Message.
    """

    base_url = f'{settings.DISCORD_API_URL}channels/'

    def __init__(self, channel, id, *, response=None):
        self.id = id

        if isinstance(channel, Channel):
            self.channel = channel
        else:
            self.channel = Channel(channel)

        self.base_url = f'{self.base_url}{self.channel.id}/messages'

        super().__init__(self.get_url(), response=response)
        self.type = MessageTypes(self.type)

    def get_url(self, url=None):
        return f'{self.base_url}/{self.id}'

    def __str__(self):
        return f'({self.id}): {self.content}'

    def __repr__(self):
        return self.__str__()
