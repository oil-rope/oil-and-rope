from discord.ext import commands
from django.utils.translation import gettext_lazy as _


class Miscellaneous(commands.Cog, name='Miscellaneous'):
    """
    Management commands, help and configuration.
    """

    def __init__(self, bot: commands.Bot, *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)

    @commands.command()
    async def shutdown(self, ctx: commands.Context):
        """
        Shutdowns bot.
        """

        if await self.bot.is_owner(ctx.author):
            msg = _('shutting down')
            await ctx.send(f'{msg.capitalize()}...')
            await self.bot.close()
        else:
            msg = _('you don\'t have permission to perform this command')
            await ctx.send(f'{msg.capitalize()}.')
