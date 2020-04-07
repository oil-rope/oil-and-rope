import pytest
from model_bakery import baker

from bot.models import DiscordUser, DiscordServer


@pytest.fixture(scope='function', autouse=False)
def discord_user():
    instance = baker.make(DiscordUser)
    return instance


@pytest.fixture(scope='function', autouse=False)
def discord_server():
    instance = baker.make(DiscordServer)
    return instance
