import pytest
from django.apps import apps
from faker.proxy import Faker
from model_bakery import baker

from bot.commands.roleplay import WorldsCommand
from bot.models import DiscordUser
from bot.utils import get_url_from
from common.constants.models import PLACE_MODEL, USER_MODEL
from common.tools.sync import async_get
from roleplay.enums import SiteTypes
from tests.bot.helpers import mocks

Place = apps.get_model(PLACE_MODEL)
User = apps.get_model(USER_MODEL)

fake = Faker()


class TestWorldsCommand:
    command = WorldsCommand

    @pytest.fixture(scope='function')
    def user(self):
        user = baker.make(User)
        return user

    @pytest.fixture(scope='function')
    def registered_author(self, user):
        author = mocks.MemberMock()
        discord_user = baker.make(DiscordUser, id=author.id)
        discord_user.user = user
        discord_user.save()
        return author

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
    async def test_list_private_ok(self, ctx, registered_author, user):
        baker.make(Place, 2, user=user, owner=user)
        ctx.author = registered_author
        command = self.command(ctx, 'list', 'private')
        await command.run()
        worlds = await command.get_private_worlds(user)

        worlds = await command.get_list_of_worlds_as_string(worlds)
        list_of_worlds = f'Here\'s a list of your worlds: {worlds}.'

        mocks.MemberMock.send.assert_called()
        mocks.MemberMock.send.assert_called_with(list_of_worlds)

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
        baker.make(Place, 2, owner=None, user=None, site_type=SiteTypes.WORLD)
        command = self.command(ctx, 'list', 'public')
        await command.run()

        worlds = await command.get_community_worlds()
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

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_remove_ok(self, ctx, registered_author, user, mocker):
        baker.make(Place, 3, user=user, owner=user)
        ctx.author = registered_author
        # `Select world to remove`, `confirm?`
        ctx.bot = mocks.ClientMock(wait_for_anwsers=['0', 'yes'])
        command = self.command(ctx, 'remove')
        worlds = await command.get_own_worlds_as_values(user)
        deleted_world = worlds[0]
        await command.run()

        with pytest.raises(Place.DoesNotExist):
            await async_get(Place, pk=deleted_world['pk'])

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_remove_ko(self, ctx, registered_author, user, mocker):
        baker.make(Place, 3, user=user, owner=user)
        ctx.author = registered_author
        # `Select world to remove`, `confirm?`
        ctx.bot = mocks.ClientMock(wait_for_anwsers=['0', 'no'])
        command = self.command(ctx, 'remove')
        worlds = await command.get_own_worlds_as_values(user)
        deleted_world = worlds[0]
        await command.run()

        await async_get(Place, pk=deleted_world['pk'])

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_remove_messages_ok(self, ctx, registered_author, user, mocker):
        baker.make(Place, 3, user=user, owner=user)
        ctx.author = registered_author
        # `Select world to remove`, `confirm?`
        ctx.bot = mocks.ClientMock(wait_for_anwsers=['0', 'yes'])
        command = self.command(ctx, 'remove')
        deleted_world = await command.get_own_worlds_as_values(user)
        world = await command.get_world(deleted_world[0]['pk'])
        url = await get_url_from('roleplay:world_delete', kwargs={'pk': world.pk})
        await command.run()

        calls = [
            # We avoid embed because object hashing
            mocker.call(f'Are you sure you want to delete {world}? [yes/no]'),
            mocker.call(f'You can perform this action via web: {url}'),
            mocker.call(f'{world} deleted.')
        ]

        mocks.MemberMock.send.assert_called()
        # `Embed`, `confirmation`, `web message`, `world deleted`
        assert mocks.MemberMock.send.call_count == 4
        assert all(call in mocks.MemberMock.send.mock_calls for call in calls)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_remove_messages_ko(self, ctx, registered_author, user, mocker):
        baker.make(Place, 3, user=user, owner=user)
        ctx.author = registered_author
        # `Select world to remove`, `confirm?`
        ctx.bot = mocks.ClientMock(wait_for_anwsers=['0', 'no'])
        command = self.command(ctx, 'remove')
        deleted_world = await command.get_own_worlds_as_values(user)
        world = await command.get_world(deleted_world[0]['pk'])
        url = await get_url_from('roleplay:world_delete', kwargs={'pk': world.pk})
        await command.run()

        calls = [
            # We avoid embed because object hashing
            mocker.call(f'Are you sure you want to delete {world}? [yes/no]'),
            mocker.call(f'You can perform this action via web: {url}'),
            mocker.call('Okay!')
        ]

        mocks.MemberMock.send.assert_called()
        # `Embed`, `confirmation`, `web message`, `world deleted`
        assert mocks.MemberMock.send.call_count == 4
        assert all(call in mocks.MemberMock.send.mock_calls for call in calls)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_remove_timeout_on_selection_ko(self, ctx, registered_author, user, mocker):
        baker.make(Place, user=user, owner=user)
        ctx.author = registered_author
        ctx.bot = mocks.ClientMock(raise_timeout=[True])
        command = self.command(ctx, 'remove')
        await command.run()

        timeout_msg = 'Sorry, you took so long to reply.'

        mocks.MemberMock.send.assert_called()
        # `Embed`, `timeout`
        assert mocks.MemberMock.send.call_count == 2
        mocks.MemberMock.send.assert_called_with(timeout_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_remove_timeout_on_confimation_ko(self, ctx, registered_author, user, mocker):
        baker.make(Place, user=user, owner=user)
        ctx.author = registered_author
        ctx.bot = mocks.ClientMock(wait_for_anwsers=['0'], raise_timeout=[False, True])
        command = self.command(ctx, 'remove')
        await command.run()

        timeout_msg = 'Sorry, you took so long to reply.'

        mocks.MemberMock.send.assert_called()
        # `Embed`, `confirmation`, `web message`, `timeout`
        assert mocks.MemberMock.send.call_count == 4
        mocks.MemberMock.send.assert_called_with(timeout_msg)
