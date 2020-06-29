import os
from tempfile import NamedTemporaryFile

import pytest
from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from faker.proxy import Faker
from model_bakery import baker
from PIL import Image

from bot.commands.roleplay import WorldsCommand
from bot.models import DiscordUser
from bot.utils import get_url_from
from common.constants.models import PLACE_MODEL, USER_MODEL
from common.tools.sync import async_create, async_get
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

    @pytest.fixture(scope='function')
    def image(self):
        tmp_file = NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        image_file = tmp_file.name
        Image.new('RGB', (30, 60), color='red').save(image_file)

        with open(image_file, 'rb') as image_content:
            image = SimpleUploadedFile(name=image_file, content=image_content.read(), content_type='image/jpeg')
        os.remove(image_file)
        return image

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
        await async_create(Place, user=user, owner=user, site_type=SiteTypes.WORLD)
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
        await async_create(Place, user=user, owner=user, site_type=SiteTypes.WORLD)
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
        await async_create(Place, user=user, owner=user, site_type=SiteTypes.WORLD)
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
        await async_create(Place, user=user, owner=user, site_type=SiteTypes.WORLD)
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

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_create_public_ok(self, ctx, registered_author, image, mocker):
        ctx.author = registered_author
        name = fake.word()
        description = fake.paragraph()
        ctx.bot = mocks.ClientMock(
            wait_for_anwsers=[
                mocks.MessageMock(content=name),
                mocks.MessageMock(content=description),
                mocks.MessageMock(files=[image])
            ]
        )
        command = self.command(ctx, 'create', 'public')
        await command.run()

        world_create = await sync_to_async(Place.objects.first)()
        create_url = await get_url_from('roleplay:world_create')
        edit_url = await get_url_from('roleplay:world_detail', kwargs={'pk': world_create.pk})
        calls = [
            mocker.call(f'Remember you can perform this action via web: {create_url}'),
            mocker.call('First we need a name'),
            mocker.call('Now tell us about your world, a description (You can avoid this by writting \'no\')'),
            mocker.call('Maybe an image? (You can avoid this by writting \'no\')'),
            mocker.call('Congrats! Your world have been created!'),
            mocker.call(f'Check it out here: {edit_url}'),
        ]
        assert mocks.MemberMock.send.call_count == 6
        assert all(call in mocks.MemberMock.send.mock_calls for call in calls)

        assert world_create.name == name
        assert world_create.description == description
        assert world_create.user is None

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_create_public_unregistered_ko(self, ctx, mocker):
        command = self.command(ctx, 'create', 'public')
        await command.run()

        url = await get_url_from('registration:register')
        unregistered_msg = f'Seems like you are not registered. You can do it in 5 minutes {url}'

        assert mocks.MemberMock.send.call_count == 1
        mocks.MemberMock.send.assert_called_with(unregistered_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_create_timeouts_ko(self, ctx, registered_author):
        ctx.author = registered_author
        answers = [fake.word(), 'no', 'no']
        ctx.bot = mocks.ClientMock(
            wait_for_anwsers=answers,
            raise_timeout=[True]
        )
        timeout_msg = 'Sorry, you took so long to reply.'
        command = self.command(ctx, 'create')
        await command.run()

        # `web`, `name`, `timeout`
        assert mocks.MemberMock.send.call_count == 3
        mocks.MemberMock.send.assert_called_with(timeout_msg)

        # Reset calls
        mocks.MemberMock.send.call_count = 0
        ctx.bot = mocks.ClientMock(
            wait_for_anwsers=answers,
            raise_timeout=[False, True]
        )
        command = self.command(ctx, 'create')
        await command.run()

        # `web`, `name`, `description`, `timeout`
        assert mocks.MemberMock.send.call_count == 4
        mocks.MemberMock.send.assert_called_with(timeout_msg)

        # Reset calls
        mocks.MemberMock.send.call_count = 0
        ctx.bot = mocks.ClientMock(
            wait_for_anwsers=answers,
            raise_timeout=[False, False, True]
        )
        command = self.command(ctx, 'create')
        await command.run()

        # `web`, `name`, `description`, `image`, `timeout`
        assert mocks.MemberMock.send.call_count == 5
        mocks.MemberMock.send.assert_called_with(timeout_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_create_image_too_big_ko(self, ctx, registered_author, image):
        image.size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE + fake.random_int()
        ctx.author = registered_author
        name = fake.word()
        description = fake.paragraph()
        ctx.bot = mocks.ClientMock(
            wait_for_anwsers=[
                mocks.MessageMock(content=name),
                mocks.MessageMock(content=description),
                mocks.MessageMock(files=[image])
            ]
        )
        command = self.command(ctx, 'create', 'public')
        await command.run()

        image_too_big_msg = 'Image too big.'
        mocks.MemberMock.send.assert_called_with(image_too_big_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_create_image_not_sent_ko(self, ctx, registered_author, image):
        ctx.author = registered_author
        name = fake.word()
        description = fake.paragraph()
        ctx.bot = mocks.ClientMock(
            wait_for_anwsers=[
                mocks.MessageMock(content=name),
                mocks.MessageMock(content=description),
                mocks.MessageMock(content=fake.word())
            ]
        )
        command = self.command(ctx, 'create', 'public')
        await command.run()

        image_too_big_msg = 'You didn\t send an image.'
        mocks.MemberMock.send.assert_called_with(image_too_big_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_create_only_name_ok(self, ctx, registered_author):
        ctx.author = registered_author
        name = fake.word()
        ctx.bot = mocks.ClientMock(
            wait_for_anwsers=[mocks.MessageMock(content=name), 'no', 'no']
        )
        command = self.command(ctx, 'create', 'public')
        await command.run()
        created_world = await sync_to_async(Place.objects.first)()

        assert created_world.name == name
        assert created_world.description is None
        assert bool(created_world.image) is False
