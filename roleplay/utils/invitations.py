from django.core.signing import TimestampSigner
from django.utils.translation import gettext_lazy as _

from common.templatetags.string_utils import capfirstletter as cfl
from common.tools import HtmlThreadMail, get_token


def send_session_invitations(session, request, emails, subject=None, signer=None):
    """
    Sends a session invitation to each email in a list.

    Parameters
    ----------
    session: :class:`~roleplay.models.Session`
        The session to invite.
    request: :class:`~django.http.request.HttpRequest`
        The request to use to generate the invitation link and get user.
    emails: :class:`list` of :class:`str`
        The list of emails to send the invitation to.
    subject: Optional[:class:`str`]
        The subject of the invitation.
    signer: Optional[:class:`~django.core.signing.TimestampSigner` or :class:`~django.core.signing.Signer`]
        The signer to use to generate the invitation link.
    """

    if not subject:
        subject = cfl(_('a quest for you!'))

    if not signer:
        signer = TimestampSigner()

    for email in emails:
        HtmlThreadMail(
            template_name='email_templates/invitation_email.html',
            subject=subject,
            to=[email],
            request=request,
            context={
                'object': session,
                'user': request.user,
                'token': get_token(email, signer),
            },
        ).send()
