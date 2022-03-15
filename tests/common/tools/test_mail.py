import time

from django.core import mail
from django.test import RequestFactory, TestCase

from common.tools import mail as common_mail
from common.utils import create_faker

fake = create_faker()


class HtmlThreadMail(TestCase):
    mail_class = common_mail.HtmlThreadMail

    def setUp(self):
        self.to = [fake.email()]
        self.template_name = 'email_templates/email_layout.html'
        self.email = self.mail_class(template_name=self.template_name, to=self.to)

    def test_email_sent_ok(self):
        self.email.send()
        while self.email.thread.is_alive():
            print("Thread no done yet.")
            time.sleep(.5)
        self.assertEqual(1, len(mail.outbox), 'Email has not been sent.')

    def test_email_sent_with_request_ok(self):
        rf = RequestFactory()
        rq = rf.get('/', HTTP_HOST='testserver')
        email = self.mail_class(template_name=self.template_name, to=self.to, request=rq)
        email.send()
        while email.thread.is_alive():
            print("Thread no done yet.")
            time.sleep(.5)
        self.assertEqual(1, len(mail.outbox), 'Email has not been sent.')

    def test_email_sent_with_context_ok(self):
        email = self.mail_class(template_name=self.template_name, to=self.to, context={fake.word(): fake.word()})
        email.send()
        while email.thread.is_alive():
            print("Thread no done yet.")
            time.sleep(.5)
        self.assertEqual(1, len(mail.outbox), 'Email has not been sent.')
