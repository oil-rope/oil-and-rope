import discord
from discord.ext import commands

from core.exceptions import OilAndRopeException
from roleplay.utils.dice import roll_dice


class Roleplay(commands.Cog, name='Roleplay'):
    """
    Roleplay commands such a dice rolling, character sheet editing, world building...
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

    @commands.command()
    async def linkchannel(self, ctx: commands.Context, name: str = ''):
        """
        Links current channel to Campaign.
        This campaign can be passed as `name` or selected by reacting to the embed message.

        Parameters
        ----------
        name: Optional
            Name of the campaign.
            E.g. ..linkchannel "My Campaign"
        """

        await ctx.send('This command is not implemented yet.')
