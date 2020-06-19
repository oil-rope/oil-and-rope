import time

from django.core import mail
from django.template.loader import render_to_string
from django.test import TestCase
from faker import Faker

from common.tools import mail as common_mail


# noinspection DuplicatedCode
class ThreadMail(TestCase):
    mail_class = common_mail.ThreadMail

    def setUp(self):
        self.faker = Faker()
        self.to = [self.faker.email()]
        self.body = self.faker.paragraph()
        self.email = self.mail_class(body=self.body, to=self.to)

    def test_email_sent_ok(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            self.email.send()
            while self.email.is_alive():
                print("Thread no done yet.")
                time.sleep(.5)
            self.assertEqual(1, len(mail.outbox), 'Email has not been sent.')

    def test_email_content_ok(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            self.email.send()
            while self.email.is_alive():
                print("Thread no done yet.")
                time.sleep(.5)
            self.assertEqual(self.body, mail.outbox[0].body, 'Email does not match body.')
            self.assertEqual(self.to, mail.outbox[0].to, 'Receiver is incorrect.')


# noinspection DuplicatedCode
class HtmlThreadMail(TestCase):
    mail_class = common_mail.HtmlThreadMail

    def setUp(self):
        self.faker = Faker()
        self.to = [self.faker.email()]
        self.template_name = 'email_templates/email_layout.html'
        self.email = self.mail_class(template_name=self.template_name, to=self.to)

    def test_email_sent_ok(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            self.email.send()
            while self.email.is_alive():
                print("Thread no done yet.")
                time.sleep(.5)
            self.assertEqual(1, len(mail.outbox), 'Email has not been sent.')
