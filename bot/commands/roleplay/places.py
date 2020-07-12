import asyncio
from distutils.util import strtobool as to_bool

import discord
from channels.db import database_sync_to_async
from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from bot import utils
from bot.exceptions import OilAndRopeException
from bot.utils import get_url_from
from roleplay.enums import SiteTypes

from ... import enums
from ..checkers import answer_in_list, is_author, is_no, is_yes_or_no, multiple_checks


class WorldsCommand:
    """
    This command handles either `list`, `create` and `remove` actions for :class:`Place`.

    Parameters
    ----------
    ctx: :class:`discord.ext.commands.Context`
        The context where command is called.
    action: :class:`enums.Actions`
        Action to perform.
    second_action: :class:`str`
        Can be either 'public' or 'private'.
    """

    def __init__(self, ctx, action=enums.Actions.list, second_action=None):
        self.ctx = ctx
        self.action = action
        if not second_action:
            second_action = 'private'
        self.second_action = second_action
        self.handler = self.dispatch()

    def dispatch(self):
        """
        Selects the correct handler depending on the given action.
        """

        try:
            self.action = enums.Actions(self.action)
            handler = getattr(self, f'{self.action}')
        except (AttributeError, ValueError):
            handler = self.invalid_option
        return handler

    async def invalid_option(self):
        """
        When given option is not in the list.
        """

        options = ', '.join(f'`{action.value}`' for action in enums.Actions)
        msg = _('Invalid option. Supported options are %(options)s') % {'options': options}
        await self.ctx.channel.send(f'{msg}.')

    async def unregistered_user(self):
        """
        When user is not found.
        """

        url = await get_url_from('registration:register')
        msg = _('Seems like you are not registered. You can do it in 5 minutes %(url)s') % {'url': url}
        await self.ctx.author.send(msg)

    async def time_out(self, author):
        """
        User took too long to answer.
        """

        await author.send(_('Sorry, you took so long to reply') + '.')

    @database_sync_to_async
    def get_community_worlds(self):
        Place = apps.get_model('roleplay.Place')
        worlds = Place.objects.community_places().filter(site_type=SiteTypes.WORLD).order_by('name')
        return worlds

    @database_sync_to_async
    def get_private_worlds(self, user):
        Place = apps.get_model('roleplay.Place')
        worlds = Place.objects.user_places(user).order_by('name')
        return worlds

    @database_sync_to_async
    def get_own_worlds_as_values(self, user, values=['pk', 'name']):
        Place = apps.get_model('roleplay.Place')
        worlds = Place.objects.own_places(user).values(*values)
        return worlds

    @database_sync_to_async
    def get_own_worlds_as_values_list(self, user, values=['pk'], flat=True):
        Place = apps.get_model('roleplay.Place')
        worlds = Place.objects.own_places(user).values_list(*values, flat=flat)
        return worlds

    @database_sync_to_async
    def check_world_existance(self, worlds):
        return worlds.exists()

    @database_sync_to_async
    def get_list_of_worlds_as_string(self, worlds):
        return ', '.join(f'*{world.name}*' for world in worlds)

    @database_sync_to_async
    def get_world(self, pk):
        Place = apps.get_model('roleplay.Place')
        return Place.objects.get(pk=pk)

    @database_sync_to_async
    def delete_world(self, pk):
        Place = apps.get_model('roleplay.Place')
        Place.objects.get(pk=pk).delete()

    @database_sync_to_async
    def create_world(self, **data):
        Place = apps.get_model('roleplay.Place')
        return Place.objects.create(**data)

    async def get_worlds_embed(self, worlds):
        title = _('Which world would you like to delete?')
        body = render_to_string(template_name='bot/templates/place_list.txt', context={'object_list': worlds})
        # str(title) because of proxy problems
        embed = discord.Embed(title=str(title), description=body)
        return embed

    async def send_web_remove_message(self, pk, author):
        url = await get_url_from('roleplay:world_delete', kwargs={'pk': pk})
        msg = _('You can perform this action via web: %(url)s') % {'url': url}
        await author.send(msg)

    async def send_web_create_message(self, author):
        url = await get_url_from('roleplay:world_create')
        msg = _('Remember you can perform this action via web: %(url)s') % {'url': url}
        await author.send(msg)

    async def send_web_detail_message(self, author, pk):
        url = await get_url_from('roleplay:world_detail', kwargs={'pk': pk})
        msg = _('Check it out here: %(url)s') % {'url': url}
        await author.send(msg)

    async def get_image_from_message(self, message, author):
        if len(message.attachments) == 0:
            await author.send(_('You didn\t send an image') + '.')
            raise OilAndRopeException('Image no sent.')
        image = message.attachments[0]
        if image.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            await author.send(_('Image too big') + '.')
            raise OilAndRopeException('Image is too big.')
        else:
            return ContentFile(await image.read(), name=image.filename)

    async def _handle_image(self, msg):
        author = msg.author
        if not is_no()(msg):
            image = await self.get_image_from_message(msg, author)
            return image
        return None

    async def list(self):
        """
        Give a list of user's worlds.
        If user is None list all public worlds.
        """

        author = self.ctx.author

        if self.second_action == 'public':
            worlds = await self.get_community_worlds()
        else:
            discord_user = await utils.get_or_create_discord_user(author)
            web_user = discord_user.user
            if not web_user:
                await self.unregistered_user()
                return
            worlds = await self.get_private_worlds(web_user)

        worlds_existance = await self.check_world_existance(worlds)
        if worlds_existance:
            list_of_worlds = await self.get_list_of_worlds_as_string(worlds)
            msg = _('Here\'s a list of your worlds: %(worlds)s') % {'worlds': list_of_worlds}
        else:
            msg = _('Seems like there isn\'t any world yet')
        await author.send(f'{msg}.')

    async def remove(self):
        """
        Allows the user to delete one of its worlds.
        """

        author = self.ctx.author
        bot = self.ctx.bot

        discord_user = await utils.get_or_create_discord_user(author)
        web_user = discord_user.user
        if not web_user:
            await self.unregistered_user()
            return
        worlds = await self.get_own_worlds_as_values(web_user)
        worlds_existance = await self.check_world_existance(worlds)

        if not worlds_existance:
            msg = _('Seems like you don\'t have any world yet') + '.'
            await author.send(msg)
            return

        embed = await self.get_worlds_embed(worlds)
        await author.send(embed=embed)

        try:
            worlds = await self.get_own_worlds_as_values_list(web_user)
            worlds = {str(index): world for index, world in enumerate(worlds)}
            check = multiple_checks(is_author(author), answer_in_list(worlds))
            msg = await bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await self.time_out(author)
            return

        index = msg.content
        pk = worlds[index]
        selected_place = await self.get_world(pk)
        msg = _('Are you sure you want to delete %(place)s?') % {'place': selected_place}
        msg += ' [{}/{}]'.format(_('yes'), _('no'))
        await author.send(msg)

        await self.send_web_remove_message(selected_place.pk, author)

        try:
            check = multiple_checks(is_author(author), is_yes_or_no())
            msg = await bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await self.time_out(author)
            return

        proceed_delete = to_bool(msg.content) == 1
        if proceed_delete:
            await self.delete_world(selected_place.pk)
            msg = _('%(place)s deleted') % {'place': selected_place}
            await author.send(f'{msg}.')
        else:
            msg = _('Okay!')
            await author.send(msg)

    async def create(self):
        """
        Allows the user to create a world.
        """

        author = self.ctx.author
        bot = self.ctx.bot
        data = {}

        discord_user = await utils.get_or_create_discord_user(author)
        web_user = discord_user.user
        if not web_user:
            await self.unregistered_user()
            return

        data['owner'] = web_user
        data['user'] = web_user if self.second_action == 'private' else None

        await self.send_web_create_message(author)

        msg = _('First we need a name')
        await author.send(msg)
        try:
            msg = await bot.wait_for('message', check=is_author(author), timeout=60.0)
            data['name'] = msg.content
        except asyncio.TimeoutError:
            await self.time_out(author)
            return

        msg = _('Now tell us about your world, a description (You can avoid this by writting \'no\')')
        await author.send(msg)
        try:
            msg = await bot.wait_for('message', check=is_author(author), timeout=60.0)
            if not is_no()(msg):
                data['description'] = msg.content
        except asyncio.TimeoutError:
            await self.time_out(author)
            return

        msg = _('Maybe an image? (You can avoid this by writting \'no\')')
        await author.send(msg)
        try:
            msg = await bot.wait_for('message', check=is_author(author), timeout=60.0)
            image = await self._handle_image(msg)
            data['image'] = image
        except asyncio.TimeoutError:
            await self.time_out(author)
            return
        except OilAndRopeException:
            return

        data['site_type'] = SiteTypes.WORLD
        world = await self.create_world(**data)
        await author.send(_('Congrats! Your world have been created!'))
        await self.send_web_detail_message(author, world.pk)

    async def run(self):
        await self.handler()
