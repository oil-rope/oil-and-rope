import asyncio
from unittest import mock

from django.conf import settings
from faker import Faker

fake = Faker()


class ClientMock(mock.MagicMock):

    data = {
        'id': fake.random_int(),
        'display_name': fake.user_name(),
        'discriminator': fake.random_int(1000, 10000),
        'locale': fake.country_code(),
        'avatar_url': fake.image_url(),
        'premium_since': fake.boolean(),
        'created_at': fake.date_time_this_century(),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **self.data, **kwargs)
        self.ignore_check_wait_for = kwargs.pop('ignore_check_wait_for', False)
        self.wait_for_default = kwargs.pop('wait_for_default', fake.paragraph())

    async def _wait_for(self, event, *, check=None):
        message = mock.MagicMock()
        message.content = self.wait_for_default

        if self.ignore_check_wait_for:
            return message

    async def wait_for(self, event, *, check=None, timeout=None):
        msg = await asyncio.wait_for(self._wait_for(event, check=check), timeout=timeout)
        return msg


class MemberMock(ClientMock):

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None,
                   delete_after=None, nonce=None, allowed_mentions=None):
        return MessageMock(content)


class RegionMock(mock.MagicMock):

    data = {
        'value': fake.country_code()
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **self.data, **kwargs)


class GuildMock(mock.MagicMock):

    data = {
        'id': fake.random_int(),
        'region': RegionMock(),
        'icon_url': fake.image_url(),
        'owner': MemberMock(),
        'description': fake.paragraph(),
        'member_count': fake.random_int(),
        'created_at': fake.date_time_this_century(),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **self.data, **kwargs)
        self.name = fake.word()
        self.owner_id = self.owner.id


class TextChannelMock(mock.MagicMock):

    data = {
        'id': fake.random_int(),
        'position': fake.random_int(),
        'topic': fake.word(),
        'created_at': fake.date_time_this_century(),
        'guild': GuildMock()
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **self.data, **kwargs)
        self.name = fake.word()

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        return MessageMock(content=content)

    def is_nsfw(self):
        return fake.boolean()

    def is_news(self):
        return fake.boolean()


class MessageMock(mock.MagicMock):
    data = {
        'id': fake.random_int(),
        'author': MemberMock(),
        'content': fake.word(),
        'channel': TextChannelMock(),
        'guild': GuildMock(),
        'created_at': fake.date_time()
    }

    def __init__(self, content=None):
        if content:
            self.data['content'] = content
        super().__init__(**self.data)


class ContextMock(mock.MagicMock):
    data = {
        'author': MemberMock(),
        'channel': TextChannelMock(),
        'prefix': settings.BOT_COMMAND_PREFIX,
        'bot': ClientMock()
    }

    def __init__(self):
        super().__init__(**self.data)
