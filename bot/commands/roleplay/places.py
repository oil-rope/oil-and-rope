import asyncio
import functools
from distutils.util import strtobool as to_bool

import discord
from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from bot import utils
from bot.utils import get_url_from
from common.tools.sync import async_create, async_get, async_manager_func


async def world_list(author, public=False):
    """
    Give a list of user's worlds.
    If user is None list all public worlds.
    """

    Place = apps.get_model('roleplay.Place')
    if public:
        worlds = await async_manager_func(Place, 'community_places')
    else:
        discord_user = await utils.get_or_create_discord_user(author)
        web_user = discord_user.user
        worlds = await async_manager_func(Place, 'user_places', user=web_user)

    if not worlds.exists():
        msg = _('Seems like there isn\'t any world yet') + '.'
    else:
        list_of_worlds = ', '.join(f'*{world.name}*' for world in worlds)
        msg = _('Here\'s a list of your worlds: {}').format(list_of_worlds) + '.'
    await author.send(msg)

    url = await get_url_from('roleplay:world_list')
    msg = _('Remember you can get a better display at the web: {}').format(url)
    await author.send(msg)


async def _get_world_delete_embed(user_worlds):
    """
    Fractioning functions so they are not that complex.
    """

    title = _('Which world would you like to delete?')
    body = render_to_string(template_name='bot/templates/place_list.txt', context={'object_list': user_worlds})
    # str(title) because of proxy problems
    embed = discord.Embed(title=str(title), description=body)
    return embed


# TODO: Refactor (Too complex)
async def world_delete(author, bot):  # noqa
    """
    Allows the user to delete one of its worlds.
    """

    Place = apps.get_model('roleplay.Place')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    discord_user = await utils.get_or_create_discord_user(author)
    try:
        web_user = await utils.async_get(User, pk=discord_user.user_id)
    except User.DoesNotExist:
        msg = _('Seems like you don\' have a user.')
        await author.send(msg)
        url = await get_url_from('registration:register')
        msg = _('You can register on the website {}').format(url)
        await author.send(msg)
        return

    # Since we need to deal with async funcs this mess is needed.
    user_worlds = await async_manager_func(Place, 'own_places', user=web_user)
    filter_func = functools.partial(user_worlds.values, 'pk', 'name')
    user_worlds = await sync_to_async(filter_func)()

    if not user_worlds.exists():
        msg = _('Seems like you don\'t have any world yet') + '.'
        await author.send(msg)
    else:
        # We created an embed to be more visual
        embed = await _get_world_delete_embed(user_worlds)
        await author.send(embed=embed)

        # Given option in possible options
        def check_correct_option(m):
            if m.content and m.author == author:
                return int(m.content) in range(0, len(user_worlds))
            else:
                return False

        # Wait for response
        try:
            msg = await bot.wait_for('message', check=check_correct_option, timeout=60.0)
        except asyncio.TimeoutError:
            await author.send(_('Sorry, you took so long to reply') + '.')
        else:
            index = msg.content
            selected_place = user_worlds[int(index)]
            selected_place = await async_get(Place, pk=selected_place['pk'])

            msg = _('Are you sure you want to delete {}?').format(selected_place)
            msg += ' [{}/{}]'.format(_('yes'), _('no'))
            await author.send(msg)
            url = await get_url_from('roleplay:world_delete', kwargs={'pk': selected_place.pk})
            msg = _('You can perform this action via web: {}').format(url)
            await author.send(msg)

            # Oh no... We need to nest...
            def check_affirmative(m):
                if m.content and m.author == author:
                    try:
                        # strtobool returns 0 or 1, here we make sure answer are yes, no, n, y, true, false...
                        result = to_bool(m.content)
                        return result in (0, 1)
                    # If value is something unexpected strtobool throws ValueError
                    except ValueError:
                        return False
                else:
                    return False

            try:
                msg = await bot.wait_for('message', check=check_affirmative, timeout=60.0)
            except asyncio.TimeoutError:
                await author.send(_('Sorry, you took so long to reply') + '.')
            else:
                # Processing answer
                proceed_delete = to_bool(msg.content) == 1
                if proceed_delete:
                    await sync_to_async(selected_place.delete)()
                    msg = _('{} deleted').format(selected_place) + '.'
                    await author.send(msg)
                else:
                    msg = _('Okay!')
                    await author.send(msg)


# TODO: Refactor this, please
async def world_create(author, bot, second_action='private'):  # noqa
    """
    Allows the user to create a world.
    """

    Place = apps.get_model('roleplay.Place')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    discord_user = await utils.get_or_create_discord_user(author)
    try:
        web_user = await utils.async_get(User, pk=discord_user.user_id)
    except User.DoesNotExist:
        msg = _('Seems like you don\' have a user.')
        await author.send(msg)
        url = await get_url_from('registration:register')
        msg = _('You can register on the website {}').format(url)
        await author.send(msg)
        return

    data = {
        'user': web_user if second_action == 'private' else None,
        'owner': web_user
    }

    def check_author(m): return m.author == author

    url = await get_url_from('roleplay:world_create')
    msg = _('Remember you can perform this action via web: {}').format(url)
    msg = _('First we need a name')
    await author.send(msg)
    try:
        msg = await bot.wait_for('message', check=check_author, timeout=60.0)
        data['name'] = msg.content
    except asyncio.TimeoutError:
        msg = _('Sorry you took too long to reply') + '.'
        await author.send(msg)
        return

    msg = _('Now tell us about your world, a description (You can avoid this by writting \'no\')')
    await author.send(msg)
    try:
        msg = await bot.wait_for('message', check=check_author, timeout=60.0)
        if msg.content not in ('n', 'no', 'f', 'false', 'off', '0'):
            data['description'] = msg.content
    except asyncio.TimeoutError:
        msg = _('Sorry you took too long to reply') + '.'
        await author.send(msg)
        return

    msg = _('Maybe an image? (You can avoid this by writting \'no\')')
    await author.send(msg)
    try:
        msg = await bot.wait_for('message', check=check_author, timeout=60.0)
        if msg.content not in ('n', 'no', 'f', 'false', 'off', '0'):
            image = msg.attachments[0]
            if image.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                await author.send(_('Image too big') + '.')
            data['image'] = ContentFile(await image.read(), name=image.filename)
    except asyncio.TimeoutError:
        msg = _('Sorry you took too long to reply') + '.'
        await author.send(msg)
        return

    world = await async_create(Place, **data)
    await author.send(_('Congrats! Your world have been created!'))
    url = await get_url_from('roleplay:world_detail', kwargs={'pk': world.pk})
    await author.send(_('Check it out here: {}').format(url))
