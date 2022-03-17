import discord
from discord.ext import commands
from django.utils.translation import gettext_lazy as _

from core.exceptions import OilAndRopeException
from roleplay.utils.dice import roll_dice


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


class Roleplay(commands.Cog, name='Roleplay'):
    """
    Roleplay commands such a dice rolling, character sheet editting, world building...
    """

    @commands.command()
    async def roll(self, ctx: commands.Context, roll: str):
        """
        Execute a dice roll.

        Parameters
        ----------
        roll:
            A dice roll with a correct syntax.
            E.g. `4D6`, `d20`, `2d4+1`, ...
        """

        try:
            result, rolls = roll_dice(roll)
            embed_roll = discord.Embed(
                title=f'Roll *{roll}*',
                description=f'You rolled **{result}**.',
            )
            embed_roll.set_footer(text=', '.join([f'{roll}: {result}' for roll, result in rolls.items()]))
            await ctx.send(embed=embed_roll)
        except OilAndRopeException as ex:
            await ctx.send(ex.message)
