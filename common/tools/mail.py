import threading

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from common.context_processors.utils import requests_utils


class HtmlThreadMail:
    def __init__(self, template_name, request=None, context=None, subject='', from_email=None, to=None, bcc=None):
        self.template_name = template_name
        self.request = request
        self.context = context
        self.subject = subject
        self.from_email = from_email
        self.to = to
        self.bcc = bcc
        self.thread = None

    def get_email(self):
        mail = EmailMultiAlternatives(subject=self.subject, from_email=self.from_email, to=self.to, bcc=self.bcc)
        mail.attach_alternative(self.get_body(), 'text/html')
        return mail

    def get_context_data(self):
        context = {
            'protocol': 'https',
            'domain': 'oilandrope-project.com',
        }
        if self.request:
            context.update(requests_utils(self.request))
        if self.context:
            context.update(self.context)
        return context

    def get_body(self):
        return render_to_string(template_name=self.template_name, context=self.get_context_data())

    def send(self, fail_silently=False):
        email = self.get_email()
        self.thread = threading.Thread(target=email.send, kwargs={'fail_silently': fail_silently})
        self.thread.start()
