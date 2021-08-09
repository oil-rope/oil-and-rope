import discord.ext.test as dpytest
import pytest
from discord.ext.test.backend import get_state, make_user
from discord.ext.test.factories import make_member_dict
from discord.member import Member

from bot.bot import OilAndRopeBot
from common.utils.faker import create_faker

fake = create_faker()


@pytest.fixture
def bot(event_loop):
    bot = OilAndRopeBot(loop=event_loop)
    dpytest.configure(client=bot, num_guilds=1, num_channels=1, num_members=2)
    return bot


@pytest.fixture
def member(bot):
    user = make_user(fake.user_name(), 1234)
    guild = bot.guilds[-1]
    member_data = make_member_dict(guild, user, [])
    state = get_state()
    member = Member(guild=guild, data=member_data, state=state)
    guild._add_member(member)

    return member
