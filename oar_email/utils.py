from typing import TYPE_CHECKING

from django.core.mail import send_mail
from django.http.request import HttpRequest
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from common.context_processors.utils import requests_utils
from common.templatetags.string_utils import capfirstletter as cfl
from common.utils.auth import generate_token

if TYPE_CHECKING:
    from registration.models import User


def send_confirmation_email(request: HttpRequest, user: 'User', template: str = 'email_templates/confirm_email.html'):
    """
    Sends an standard Email Confirmation mail.
    """

    context = {
        'token': generate_token(user),
        'object': user,
    }
    context.update(requests_utils(request))
    html_msg = render_to_string(template, context, request)

    subject = _('welcome to %(title)s!') % {'title': 'Oil & Rope'}
    send_mail(
        subject=cfl(subject), message='', from_email=None,
        recipient_list=[user.email], html_message=html_msg,
    )
