import random

from django.test import TestCase
from faker import Faker

from bot.commands import checkers
from tests.bot.helpers import mocks


class TestCheckers(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.member = mocks.MemberMock
        self.message = mocks.MessageMock()

    def test_is_author_ok(self):
        author = self.message.author
        check = checkers.is_author(author)(self.message)

        self.assertTrue(check)

    def test_is_author_ko(self):
        author = mocks.MemberMock()
        check = checkers.is_author(author)(self.message)

        self.assertFalse(check)

    def test_is_yes_or_no_ok(self):
        self.message.content = random.choice(['yes', 'no'])
        check = checkers.is_yes_or_no()(self.message)

        self.assertTrue(check)

    def test_is_yes_or_no_ko(self):
        self.message.content = self.faker.password()
        check = checkers.is_yes_or_no()(self.message)

        self.assertFalse(check)

    def test_is_yes_ok(self):
        self.message.content = 'yes'
        check = checkers.is_yes()(self.message)

        self.assertTrue(check)

    def test_is_yes_ko(self):
        self.message.content = self.faker.word()
        check = checkers.is_yes()(self.message)

        self.assertFalse(check)

    def test_is_no_ok(self):
        self.message.content = 'no'
        check = checkers.is_no()(self.message)

        self.assertTrue(check)

    def test_is_no_ko(self):
        self.message.content = self.faker.word()
        check = checkers.is_no()(self.message)

        self.assertFalse(check)

    def test_answer_in_list_ok(self):
        item_list = [self.faker.word() for _ in range(0, 10)]
        self.message.content = random.choice(item_list)
        check = checkers.answer_in_list(item_list)(self.message)

        self.assertTrue(check)

    def test_answer_in_list_ko(self):
        item_list = [self.faker.word() for _ in range(0, 10)]
        self.message.content = self.faker.password()
        check = checkers.answer_in_list(item_list)(self.message)

        self.assertFalse(check)

    def test_multiple_checks_ok(self):
        self.message.content = 'yes'
        check = checkers.multiple_checks(checkers.is_yes_or_no(), checkers.is_yes())(self.message)

        self.assertTrue(check)

    def test_multiple_checks_no(self):
        self.message.content = 'yes'
        check = checkers.multiple_checks(checkers.is_yes_or_no(), checkers.is_no())(self.message)

        self.assertFalse(check)
