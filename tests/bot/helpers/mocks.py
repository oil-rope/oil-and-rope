import asyncio
from io import IOBase
from unittest import mock

from asgiref.sync import async_to_sync
from discord import Attachment
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

    def __init__(self, *, wait_for_anwsers=[], ignore_checks=True, raise_timeout=False):
        super().__init__(**self.data)
        self.wait_for_anwsers = wait_for_anwsers
        self.ignore_checks = ignore_checks

        # Setup false to every answer
        if not raise_timeout:
            raise_timeout = [False for answer in self.wait_for_anwsers]
        self.raise_timeout = raise_timeout

    async def _get_wait_for_answer(self):
        try:
            content = self.wait_for_anwsers.pop(0)
            if isinstance(content, str):
                content = MessageMock(content=content)
            elif isinstance(content, IOBase):
                content = MessageMock(file=content)
            return content
        except TypeError:
            content = MessageMock(content=fake.word())
            return content

    async def _get_raise_timeout(self):
        try:
            return self.raise_timeout.pop(0)
        except TypeError:
            return False

    async def wait_for(self, event, *, check=None, timeout=None):
        if await self._get_raise_timeout():
            raise asyncio.TimeoutError

        if event == 'message':
            answer = await self._get_wait_for_answer()
            return answer

        if self.ignore_checks:
            return event

        if check(event):
            return event


class MemberMock(ClientMock):

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None,
                   delete_after=None, nonce=None, allowed_mentions=None):
        return MessageMock(content, embed=embed)


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

    def __init__(self, content=None, *, embed=None, file=[], files=[]):
        if content:
            self.data['content'] = content
        self.data.update({
            'embed': embed,
            'files': file + files
        })
        super().__init__(**self.data)

    @property
    def attachments(self):
        attachments = []
        for f in self.files:
            f = ContextAttachment(f=f, size=f.size)
            attachments.append(f)
        return attachments


class ContextAttachment(mock.MagicMock):
    data = {
        'id': fake.random_int(),
        'url': fake.url(),
        'proxy_url': fake.url()
    }

    def __init__(self, *, f=None, size=None):
        self.data['file'] = f
        if not size:
            size = f.size
        self.data['size'] = size
        self.data['filename'] = f.name

        super().__init__(**self.data)

    async def read(self, *, use_cached=False):
        return self.file.read()


class ContextMock(mock.MagicMock):
    data = {
        'author': MemberMock(),
        'channel': TextChannelMock(),
        'prefix': settings.BOT_COMMAND_PREFIX,
        'bot': ClientMock()
    }

    def __init__(self):
        super().__init__(**self.data)
