from django.test import TestCase
from faker.proxy import Faker

from bot.exceptions import HelpfulError, OilAndRopeException, PermissionsError


class TestOilAndRopeException(TestCase):
    exception = OilAndRopeException

    def setUp(self):
        self.faker = Faker()

    def test_message_ok(self):
        msg = self.faker.word()
        ex = self.exception(msg)

        self.assertEqual(msg, ex.message)

    def test_message_no_format_ok(self):
        msg = self.faker.word()
        ex = self.exception(msg)

        self.assertEqual(msg, ex.message_no_format)


class TestHelpfulError(TestCase):
    exception = HelpfulError

    def test_correct_format(self):
        """
        Translation works correctly.
        """

        msg = '\nAn error ocurred\n\tProblem: Test Error Msg\n\n\tSolution: Just keep going.\n\n'
        ex = self.exception(issue='Test Error Msg', solution='Just keep going.')
        self.assertEqual(msg, ex.message, 'Message has incorrect format.')


class TestPermissionsError(TestCase):
    exception = PermissionsError

    def test_correct_format(self):
        msg = 'Not allowed.'
        expected_msg = f'You don\'t have permission to use that command.\nMore info: {msg}'
        ex = self.exception(msg)

        self.assertEqual(expected_msg, ex.message)
