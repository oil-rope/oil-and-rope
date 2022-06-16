import random
import re
from collections import defaultdict
from typing import Optional

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.exceptions import OilAndRopeException

DICE_ROLL_PATTERN = r'^((\d+|\d*[dD]\d+)([-+](\d+|\d*[dD]\d+))*)$'
DICE_REGEX = re.compile(DICE_ROLL_PATTERN)


def is_dice_roll(roll: str) -> Optional[re.Match]:
    """
    Checks by pattern if roll is a valid dice roll.
    This includes `nDy`, `ndy` and mixes with numbers `+` and `-`.

    Parameters
    ----------
    roll: :class:`str`
        Given roll pattern.
    """

    matcher = DICE_REGEX.match(roll)
    return matcher


def roll_dice_logic(d_roll: str) -> list[int]:
    """
    This method will execute a dice roll and return the result as a list with all rolled numbers.

    Parameters
    ----------
    d_roll: :class:`str`
        Given dice roll.
        E.g. `1d20`, `4D6`, ...
    """

    escaped_d_roll = re.sub(r'[-+]', '', d_roll)
    d_number, d_face = re.split(r'[dD]', escaped_d_roll)
    d_face = int(d_face)
    d_number = int(d_number) if d_number else 1
    return [random.randint(1, d_face) for _n in range(0, d_number)]


def roll_dice(roll: str) -> tuple[int, defaultdict[str, list[int]]]:
    """
    This function separates and executes the rolling, addition and subtraction needed.
    It also checks if roll comes with `settings.BOT_COMMAND_PREFIX` and if so, it will
    remove it and strip the message to avoid dangling whitespaces.

    Parameters
    ----------
    roll: :class:`str`
        Given dice roll pattern.
    """

    if roll.startswith(f'{settings.BOT_COMMAND_PREFIX}roll'):
        roll = roll.replace(f'{settings.BOT_COMMAND_PREFIX}roll', '').strip()

    if not is_dice_roll(roll):
        msg = _('dice roll `%(roll)s` syntax is incorrect.') % {
            'roll': roll,
        }
        raise OilAndRopeException(msg.capitalize())

    # First of all we separate dice rolls since they work differently
    dice_rolls = re.findall(r'[-+]?\d*[dD]\d+', roll)
    dice_rolls_result = defaultdict(list)
    for d_roll in dice_rolls:
        dice_rolls_result[d_roll] = roll_dice_logic(d_roll)
        # NOTE: If we removed rolled dices is easier later to continue the logic
        roll = roll.replace(d_roll, '')

    # Number rolls are easier since it's just addition or subtraction
    number_rolls = re.findall(r'[-+]?\d+', roll)
    for number in number_rolls:
        dice_rolls_result[number] = [int(number)]

    final_result = 0
    for key, value in dice_rolls_result.items():
        # NOTE: Doll doesn't work with negative numbers but list of positive int, we just sum and subtract
        if key.startswith('-') and len(value) >= 1:
            final_result -= sum(value)
        else:
            final_result += sum(value)

    return final_result, dice_rolls_result
