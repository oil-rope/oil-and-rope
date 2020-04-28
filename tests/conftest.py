import pytest
from bot.models import DiscordServer, DiscordUser
from model_bakery import baker


@pytest.fixture(scope='function', autouse=False)
def discord_user():
    instance = baker.make(DiscordUser)
    return instance


@pytest.fixture(scope='function', autouse=False)
def discord_server():
    instance = baker.make(DiscordServer)
    return instance
