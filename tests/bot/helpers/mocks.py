from unittest import mock

from faker import Faker

fake = Faker()


class MemberMock(mock.MagicMock):

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

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None,
                   delete_after=None, nonce=None, allowed_mentions=None):
        return content


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

    def is_nsfw(self):
        return fake.boolean()

    def is_news(self):
        return fake.boolean()
