import pytest

from core.exceptions import OilAndRopeException
from roleplay.utils.dice import is_dice_roll, roll_dice


def test_is_dice_roll_just_dice_ok():
    roll = 'd20'

    assert is_dice_roll(roll), 'Dice roll with dice is not working'


def test_is_dice_roll_dice_and_number_ok():
    roll = '4d6'

    assert is_dice_roll(roll), 'Dice roll with dice and number of dices is not working'


def test_is_dice_roll_dice_and_large_number_ok():
    roll = '10d6'

    assert is_dice_roll(roll), 'Dice roll with dice and large number of dices is not working'


def test_is_dice_roll_just_dice_capital_ok():
    roll = 'D20'

    assert is_dice_roll(roll), 'Dice roll with dice and capital "D" is not working'


def test_is_dice_roll_dice_and_number_capital_ok():
    roll = '4D6'

    assert is_dice_roll(roll), 'Dice roll with dice, number of dices and capital "D" is not working'


def test_is_dice_roll_dice_and_large_number_capital_ok():
    roll = '10D6'

    assert is_dice_roll(roll), 'Dice roll with dice, large number of dices and capital "D" is not working'


def test_is_dice_roll_dice_and_additions_ok():
    roll = '4d6+4'

    assert is_dice_roll(roll), 'Dice roll with additions is not working'


def test_is_dice_roll_dice_and_additions_large_number_ok():
    roll = '4d6+16'

    assert is_dice_roll(roll), 'Dice roll with large number additions is not working'


def test_is_dice_roll_dice_and_subtraction_ok():
    roll = '4d6-4'

    assert is_dice_roll(roll), 'Dice roll with subtraction is not working'


def test_is_dice_roll_dice_and_subtraction_large_number_ok():
    roll = '4d6-16'

    assert is_dice_roll(roll), 'Dice roll with large number subtraction is not working'


def test_is_dice_roll_addition_multiple_roll_ok():
    roll = '4d6+2d4'

    assert is_dice_roll(roll), 'Dice roll with addition multiple roll'


def test_is_dice_roll_complex_roll_ok():
    roll = '4d6-20d2+3-D20+12'

    assert is_dice_roll(roll), 'Dice roll with complex roll is not working'


def test_is_dice_roll_incorrect_syntax_ko():
    roll = '1d20+'

    assert not is_dice_roll(roll), 'Incorrect dice roll syntax is taken as correct'


def test_dice_roll_incorrect_syntax_ko():
    roll = '1d20+'
    with pytest.raises(OilAndRopeException, match='Dice roll `.+` syntax is incorrect.'):
        roll_dice(roll)


def test_dice_roll_complex_roll_ok():
    roll = '4d6-20d2+3-D20+12-1'
    result, rolls = roll_dice(roll)

    assert isinstance(result, int)
    assert isinstance(rolls, dict)


def test_dice_roll_simple_roll_ok():
    roll = 'd20+2'
    result, rolls = roll_dice(roll)

    assert result <= 20 and result >= 3
    assert 'd20' in rolls and '+2' in rolls
