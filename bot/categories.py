import logging
import re
from random import randint

from discord.ext.commands import Cog, command
from django.utils.translation import ugettext_lazy as _

LOGGER = logging.getLogger(__name__)


class RoleplayCog(Cog, name='Roleplay'):
    """
    Commands for managing roleplay.
    """

    qualified_name = _('Roleplay')

    dice_pattern = r'(?P<dice>\d*[Dd]\d+)'
    dice_pattern_compiled = re.compile(dice_pattern)
    modifier_pattern = r'(?P<modifier>[\+\-]((\d*[dD])?\d+))'
    modifier_pattern_compiled = re.compile(modifier_pattern)
    roll_pattern = r'^{}{}*$'.format(dice_pattern, modifier_pattern)
    roll_pattern = re.compile(roll_pattern)

    def _process_roll_dice(self, number_of_rolls, dice_face):
        """
        Gets a number of rolls to do to a dice face and returns all the results.
        """

        results = []
        for n in range(0, number_of_rolls):
            results.append(randint(1, dice_face))
        return results

    def _process_roll_action(self, action, *numbers):
        """
        Executes sum or substract depending on the action.
        """

        result = 0
        for n in numbers:
            if action == '+':
                result += n
            elif action == '-':
                result -= n
        return result

    def _process_roll(self, roll: str):
        """
        Gets a roll and process it correctly returning the result

        Parameters
        ----------
        roll: :class:`str`
            The roll to process.
        """

        result = 0
        results_message = ''
        action = '+'
        sliced_roll = re.split(r'([\+\-])', roll)

        # TODO: We need a refractor in here!
        for roll in sliced_roll:
            if re.match(r'[\+\-]', roll):
                action = roll
                results_message += action
                continue
            if self.dice_pattern_compiled.match(roll):
                n_rolls, d_faces = re.split(r'[dD]', roll)
                results = self._process_roll_dice(int(n_rolls), int(d_faces))
                results_message += action.join([str(r) for r in results])
                result += self._process_roll_action(action, *results)
            else:
                results_message += roll
                roll = int(roll)
                result += self._process_roll_action(action, roll)

        return result, results_message

    @command()
    async def roll(self, ctx, roll):
        """
        Makes a roll.

        Parameters
        ----------
        roll:
            The roll. It must follow the pattern `XdY` or `xDy`.
            It can also receive `XdY+XdN-...`
        """

        roll = roll.strip().replace(' ', '')
        if not self.roll_pattern.match(roll):
            await ctx.send(_('The roll must follow the correct pattern.'))
            await ctx.send_help(self.roll)
            return
        result, roll_message = self._process_roll(roll)
        message = _('{user} rolled').format(user=ctx.author.name)
        message += ' **{roll}** *({message})*.'.format(
            roll=result,
            message=roll_message
        )
        await ctx.send(message)


class MiscellaneousCog(Cog, name='Miscellaneous'):
    """
    Commands that have special behaviour.
    """

    qualified_name = _('Miscellaneous')

    @command()
    async def shutdown(self, ctx):
        """
        If owner invokes this command bot will be shutted down.
        """

        is_owner = await ctx.bot.is_owner(ctx.author)
        if is_owner:
            msg = 'Shutting down {}...'.format(ctx.bot.user.name)
            print(msg)
            LOGGER.info(msg)
            await ctx.send(_('Shutting down') + '...')
            await ctx.bot.logout()


class UserCog(Cog, name='User'):
    """
    Commands related to user interface and managing.
    """

    qualified_name = _('User')

    @command()
    async def invite(self, ctx):
        """
        Creates an invitation to join the full Oil & Rope experience!
        """

        from .models import DiscordUser

        try:
            author = ctx.author
            DiscordUser.objects.get(id=author.id)
        except DiscordUser.DoesNotExist:
            bot = ctx.bot
            await bot.confirm_user(author.id)
        else:
            await author.send(_('You are part of the full experience already' + '!'))
