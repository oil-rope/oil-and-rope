import pytest
from django.apps import apps
from faker.proxy import Faker
from model_bakery import baker

from bot.commands.roleplay import WorldsCommand
from bot.models import DiscordUser
from bot.utils import get_url_from
from common.constants.models import PLACE_MODEL, USER_MODEL
from roleplay.enums import SiteTypes
from tests.bot.helpers import mocks

Place = apps.get_model(PLACE_MODEL)
User = apps.get_model(USER_MODEL)

fake = Faker()


class TestWorldsCommand:
    command = WorldsCommand

    @pytest.fixture(scope='function')
    def registered_author(self):
        author = mocks.MemberMock()
        user = baker.make(User)
        discord_user = baker.make(DiscordUser, id=author.id)
        discord_user.user = user
        discord_user.save()
        return author

    @pytest.fixture(scope='function')
    def user(self):
        user = baker.make(User)
        return user

    @pytest.fixture(scope='function', autouse=True)
    def text_channel_send(self, mocker):
        mocker.patch('tests.bot.helpers.mocks.TextChannelMock.send')

    @pytest.fixture(scope='function', autouse=True)
    def text_member_send(self, mocker):
        mocker.patch('tests.bot.helpers.mocks.MemberMock.send')

    @pytest.fixture(scope='function')
    def ctx(self):
        ctx = mocks.ContextMock()
        return ctx

    def test_dispatch_list_ok(self, ctx):
        command = self.command(ctx, 'list')

        assert command.handler == command.list

    def test_dispatch_create_ok(self, ctx):
        command = self.command(ctx, 'create')

        assert command.handler == command.create

    def test_dispatch_remove_ok(self, ctx):
        command = self.command(ctx, 'remove')

        assert command.handler == command.remove

    def test_dispatch_invalid_action_ok(self, ctx):
        command = self.command(ctx, fake.word())

        assert command.handler == command.invalid_option

    def test_default_second_action(self, ctx):
        command = self.command(ctx, 'list')

        assert command.second_action == 'private'

    def test_public_second_action(self, ctx):
        command = self.command(ctx, 'list', 'public')

        assert command.second_action == 'public'

    def test_private_second_action(self, ctx):
        command = self.command(ctx, 'list', 'private')

        assert command.second_action == 'private'

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_invalid_option(self, ctx):
        command = self.command(ctx, fake.word())
        await command.run()

        invalid_option_msg = 'Invalid option. Supported options are `list`, `create`, `remove`.'
        mocks.TextChannelMock.send.assert_called()
        mocks.TextChannelMock.send.assert_called_with(invalid_option_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_unregistered_user(self, ctx):
        url = await get_url_from('registration:register')
        ctx.author = mocks.MemberMock()
        command = self.command(ctx, 'list')
        await command.run()

        unregistered_user_msg = f'Seems like you are not registered. You can do it in 5 minutes {url}'
        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(unregistered_user_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_time_out(self, ctx):
        ctx.author = mocks.MemberMock()
        command = self.command(ctx, 'list')
        await command.time_out(ctx.author)

        time_out_message = 'Sorry, you took so long to reply.'
        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(time_out_message)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_list_public_empty_ko(self, ctx):
        command = self.command(ctx, 'list', 'public')
        await command.run()

        empty_msg = 'Seems like there isn\'t any world yet.'
        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(empty_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_list_private_empty_ko(self, ctx, registered_author):
        ctx.author = registered_author
        command = self.command(ctx, 'list', 'private')
        await command.run()

        empty_msg = 'Seems like there isn\'t any world yet.'
        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(empty_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_list_public_unregistered_user_ok(self, ctx):
        worlds = baker.make(Place, 2, owner=None, user=None, site_type=SiteTypes.WORLD)
        command = self.command(ctx, 'list', 'public')
        await command.run()

        worlds = await command.get_list_of_worlds_as_string(worlds)
        list_of_worlds = f'Here\'s a list of your worlds: {worlds}.'
        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(list_of_worlds)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_list_private_unregistered_user_ko(self, ctx):
        command = self.command(ctx, 'list', 'private')
        await command.run()

        url = await get_url_from('registration:register')
        unregistered_user_msg = f'Seems like you are not registered. You can do it in 5 minutes {url}'
        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(unregistered_user_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_remove_unregistered_user_ko(self, ctx):
        command = self.command(ctx, 'remove')
        await command.run()

        url = await get_url_from('registration:register')
        unregistered_user_msg = f'Seems like you are not registered. You can do it in 5 minutes {url}'
        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(unregistered_user_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_remove_empty_ko(self, ctx, registered_author):
        ctx.author = registered_author
        command = self.command(ctx, 'remove')
        await command.run()

        empty_msg = 'Seems like you don\'t have any world yet.'
        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(empty_msg)
