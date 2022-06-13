from django.conf import settings
from django.utils.translation import get_language_from_request

from common.enums import AvailableIcons, JavaScriptActions
from registration.models import Profile


def language(request):
    """
    Sets language depending on the profile.
    """

    language = get_language_from_request(request)
    content = {
        'lan': language if language else settings.LANGUAGE_CODE,
        'languages': dict(settings.LANGUAGES).keys(),
    }

    if 'session_language' in request.session:
        content['lan'] = request.session['session_language']
        return content

    user = request.user
    if not user.is_authenticated:
        return content

    # Optimization of language selector
    language = Profile.objects.filter(user_id=user.id).values_list('language', flat=True).first()
    request.session['session_language'] = language
    content['lan'] = language

    return content


def handy_settings(request):
    """
    Sets handy settings for the frontend.

    This includes:
      - TABLETOP_URL
      - BOT_COMMAND_PREFIX
      - BOT_INVITATION
      - ICONS
      - JAVASCRIPT
    """

    content = {
        'TABLETOP_URL': settings.TABLETOP_URL,
        'BOT_COMMAND_PREFIX': settings.BOT_COMMAND_PREFIX,
        'BOT_INVITATION': settings.BOT_INVITATION,
        'ICONS': {icon.name: icon.value for icon in AvailableIcons},
        'JAVASCRIPT': {js.name: js.value for js in JavaScriptActions},
    }
    return content
