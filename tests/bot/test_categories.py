from unittest import mock
from unittest.mock import call

from django.test import TestCase
from faker import Faker

from bot.categories import RoleplayCog

fake = Faker()


class TestRoleplayCog(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.cog = RoleplayCog()
        self.actions = ['+', '-']

    @mock.patch('bot.categories.randint')
    def test_process_roll_dice(self, mock_call):
        rolls = self.faker.random_int(1)
        dice_face = self.faker.random_int(1, 100)
        calls = [call(1, dice_face) for _ in range(1, rolls)]
        self.cog._process_roll_dice(rolls, dice_face)
        mock_call.assert_has_calls(calls)

    def test_process_roll_action(self):
        rolls = self.faker.random_int(1)
        dice_face = self.faker.random_int(1, 100)
        results = self.cog._process_roll_dice(rolls, dice_face)

        action = '+'
        result = self.cog._process_roll_action(action, *results)
        expected = sum(results)
        self.assertEqual(expected, result)

        action = '-'
        result = self.cog._process_roll_action(action, *results)
        expected = 0
        for n in results:
            expected -= n
        self.assertEqual(expected, result)

    def test_process_roll(self):
        rolls = self.faker.random_int(1, 10)
        dice_face_1 = self.faker.random_int(1, 100)
        dice_face_2 = self.faker.random_int(1, 100)

        # Quite simple test
        roll = '{}d{}+D{}'.format(rolls, dice_face_1, dice_face_2)
        result, results_message = self.cog._process_roll(roll)
        expected_regex = r'(\d+\+){%s}\d' % rolls
        self.assertRegex(results_message, expected_regex)

        # More complex roll
        roll_1 = self.faker.random_int(1, 10)
        dice_face_1 = self.faker.random_int(1, 100)
        modifier_1 = self.faker.random_int(1, 10)
        modifier_2 = self.faker.random_int(1, 10)
        dice_face_2 = self.faker.random_int(1, 100)
        roll = '{}d{}+{}-{}+d{}'.format(
            roll_1,
            dice_face_1,
            modifier_1,
            modifier_2,
            dice_face_2
        )
        result, results_message = self.cog._process_roll(roll)
        expected_regex = r'(\d+\+){%s}%s\-%s\+\d+' % (roll_1, modifier_1, modifier_2)
        self.assertRegex(results_message, expected_regex)
