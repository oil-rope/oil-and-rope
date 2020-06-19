import threading

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class ThreadMail(threading.Thread):

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None,
                 reply_to=None):
        super().__init__()
        self.fail_silently = False
        self.mail = mail.EmailMessage(subject, body, from_email, to, bcc,
                                      connection, attachments, headers, cc, reply_to)

    def run(self):
        self.mail.send(self.fail_silently)

    def send(self, fail_silently=False):
        self.fail_silently = fail_silently
        self.start()


class HtmlThreadMail(threading.Thread):

    def __init__(self, template_name, context=None, subject='', from_email=None, to=None):
        super().__init__()
        self.template_name = template_name
        self.subject = subject
        self.from_email = from_email
        self.to = to
        if not context:
            context = {}
        self.context = context
        self.body = self.render_body()
        self.plain_message = strip_tags(self.body)

    def run(self):
        mail.send_mail(subject=self.subject, message=self.plain_message, from_email=self.from_email,
                       recipient_list=self.to, html_message=self.body)

    def send(self):
        self.start()

    def render_body(self):
        return render_to_string(self.template_name, self.context)
