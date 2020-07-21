from django.conf import settings
from django.utils.translation import get_language_from_request

from registration.models import Profile


def language(request):
    """
    Sets language depending on the profile.
    """

    language = get_language_from_request(request)
    user = request.user
    content = {
        'lan': language if language else settings.LANGUAGE_CODE,
        'languages': dict(settings.LANGUAGES).keys(),
    }

    if not user.is_authenticated:
        return content

    if 'session_language' in request.session:
        content['lan'] = request.session['session_language']
        return content

    # Optimizacion of language selector
    language = Profile.objects.filter(user_id=user.id).values_list('language', flat=True).first()
    request.session['session_language'] = language
    content['lan'] = language

    return content
