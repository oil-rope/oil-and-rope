import asyncio
import functools
from distutils.util import strtobool as to_bool

import discord
from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from bot import utils
from bot.utils import get_url_from
from common.tools.sync import async_get, async_manager_func


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
    web_user = await utils.async_get(User, pk=discord_user.user_id)

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
