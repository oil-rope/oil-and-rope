import pytest
from model_bakery import baker

from bot.models import DiscordUser


@pytest.fixture(scope='function', autouse=False)
def discord_user():
    instance = baker.make(DiscordUser)
    return instance
