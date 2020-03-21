import logging

from discord.ext.commands import command, context

LOGGER = logging.getLogger(__name__)


@command()
async def shutdown(ctx: context.Context):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        msg = 'Shutting down {}...'.format(ctx.bot.user.name)
        print(msg)
        LOGGER.info(msg)
        await ctx.channel.send('Shutting down...')
        await ctx.bot.logout()
