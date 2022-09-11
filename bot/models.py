from typing import Optional, Union

from django.conf import settings
from requests.models import Response

from bot.enums import ChannelTypes, MessageTypes
from bot.exceptions import HelpfulError
from bot.utils import discord_api_get, discord_api_patch, discord_api_post


class ApiMixin:
    """
    This class loads content from `response` into class attributes.
    """

    id: str

    def __init__(self, url: Optional[str] = None, *, response: Optional[Response] = None):
        self.url = url

        if not self.url:
            raise HelpfulError('URL cannot be None.', 'Please declare a url or overwrite `get_url` method.')

        if response is None:
            self.response = discord_api_get(self.url)
        else:
            self.response = response
        self.json = self.response.json()

        # Magic attributes
        for key, value in self.json.items():
            setattr(self, key, value)


class User(ApiMixin):
    """
    Represents a Discord User.
    For more information see https://discord.com/developers/docs/resources/user#user-object-user-structure.
    """

    username: str
    discriminator: str
    avatar: Optional[str]
    bot: Optional[bool] = None
    system: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    banner: Optional[str] = None
    accent_color: Optional[int] = None
    locale: Optional[str] = None
    verified: Optional[bool] = None
    email: Optional[str] = None
    flags: Optional[int] = None
    premium_type: Optional[int] = None
    public_flags: Optional[int] = None

    def __init__(self, id: str, *, response: Optional[Response] = None):
        self.id = id
        self.base_url = self.get_base_url()
        super().__init__(url=self.get_url(), response=response)

    @classmethod
    def from_bot(cls):
        url = f'{cls.get_base_url()}/@me'
        response = discord_api_get(url)
        response_json = response.json()
        return cls(response_json['id'], response=response)

    @classmethod
    def get_base_url(cls):
        return f'{settings.DISCORD_API_URL}/users'

    def get_url(self):
        return f'{self.base_url}{self.id}'

    def create_dm(self):
        """
        Creates a DM with this User.
        """

        url = f'{self.base_url}/@me/channels'
        data = {
            'recipient_id': self.id
        }
        response = discord_api_post(url, data)
        json_response = response.json()
        channel_id = json_response['id']

        # Creating object from response should be faster
        return Channel(channel_id, response=response)

    def send_message(self, content, embed=None):
        """
        Sends a message to this user.
        """

        dm = self.create_dm()
        response = dm.send_message(content, embed=embed)
        return response

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.username} ({self.id})'


class Channel(ApiMixin):
    """
    Represents a Discord Channel.
    For more information see https://discord.com/developers/docs/resources/channel#channel-object-channel-structure.
    """

    type: int
    guild_id: Optional[int] = None
    position: Optional[int] = None
    permission_overwrites: Optional[list] = None
    name: Optional[str] = None
    topic: Optional[str] = None
    nsfw: Optional[bool] = None
    last_message_id: Optional[str] = None
    bitrate: Optional[int] = None
    user_limit: Optional[int] = None
    rate_limit_per_user: Optional[int] = None
    # TODO In order for this to properly transform in user we need parse once received
    recipients: Optional[list[Union[dict, User]]] = None
    icon: Optional[str] = None
    owner_id: Optional[str] = None
    application_id: Optional[str] = None
    parent_id: Optional[str] = None
    last_pin_timestamp: Optional[str] = None
    rtc_region: Optional[str] = None
    video_quality_mode: Optional[int] = None
    message_count: Optional[int] = None
    member_count: Optional[int] = None
    thread_metadata: Optional[dict] = None
    member: Optional[dict] = None
    default_auto_archive_duration: Optional[int] = None
    permissions: Optional[str] = None
    flags: Optional[int] = None
    total_message_sent: Optional[int] = None
    available_tags: Optional[list[dict]] = None
    applied_tags: Optional[list[str]] = None
    default_reaction_emoji: Optional[dict] = None
    default_thread_rate_limit_per_user: Optional[int] = None

    def __init__(self, id: str, *, response: Optional[Response] = None):
        self.id = id
        self.base_url = self.get_base_url()

        super().__init__(self.get_url(), response=response)
        self.channel_type = ChannelTypes(self.type)

    @classmethod
    def get_base_url(cls):
        return f'{settings.DISCORD_API_URL}/channels'

    def get_url(self):
        return f'{self.base_url}{self.id}'

    def send_message(self, content, embed=None):
        url = f'{self.url}/messages'
        data = {
            'content': content
        }

        if embed:
            data['embed'] = embed.data

        response = discord_api_post(url, data)
        msg_id = response.json()['id']

        # Creating message from given response should be faster
        msg = Message(self, msg_id, embed=embed, response=response)
        return msg

    def __str__(self):
        if self.name:
            return f'Channel {self.name} ({self.id})'
        return f'Channel {self.channel_type.name} ({self.id})'

    def __repr__(self):
        return self.__str__()


class Message(ApiMixin):
    """
    Represents a Discord Message.

    Parameters
    ----------
    channel: :class:`Channel` or :class:`str` or :class:`int`
        Instance of channel or ID.
    id: :class:`str` or :class:`int`
        ID of the message.
    response: :class:`requests.models.Response`
        Response attached to this message.
    """

    def __init__(self, channel, id, *, embed=None, response=None):
        self.base_url = self.get_base_url()
        if isinstance(channel, Channel):
            self.channel = channel
        else:
            self.channel = Channel(channel)
        self.base_url = f'{self.base_url}{self.channel.id}/messages'
        self.id = id
        self.embed = embed

        super().__init__(self.get_url(), response=response)
        self.type = MessageTypes(self.type)

    def edit(self, content):
        """
        Edits the given message.
        """

        url = f'{self.base_url}/{self.id}'
        data = {
            'content': content
        }
        response = discord_api_patch(url, data)

        return Message(self.channel, self.id, response=response)

    @classmethod
    def get_base_url(cls):
        return f'{settings.DISCORD_API_URL}channels/'

    def get_url(self, url=None):
        return f'{self.base_url}/{self.id}'

    def __str__(self):
        return f'({self.id}): {self.content}'

    def __repr__(self):
        return self.__str__()
