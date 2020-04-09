from django.conf import settings


def language(request):
    """
    Sets language depending on the profile.
    """

    content = {
        'lan': settings.LANGUAGE_CODE,
        'languages': dict(settings.LANGUAGES).keys(),
    }

    if request.user.is_authenticated:
        profile = request.user.profile
        content['lan'] = profile.language
        return content
    return content
