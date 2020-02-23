from django.test import TestCase

from bot.bot.exceptions import HelpfulError


class HelpfulErrorTest(TestCase):
    """
    Checks if HelpfulError is raised correctly.
    """

    def test_correct_format(self):
        """
        Translation works correctly.
        """

        msg = "\nAn error ocurred\n\tProblem: Test Error Msg\n\n\tSolution: Just keep going.\n\n"
        ex = HelpfulError(issue="Test Error Msg", solution="Just keep going.")
        self.assertEqual(msg, ex.message, "Message has incorrect format.")
