from django.conf import settings

from registration.models import Profile


def language(request):
    """
    Sets language depending on the profile.
    """

    content = {
        'lan': settings.LANGUAGE_CODE,
        'languages': dict(settings.LANGUAGES).keys(),
    }

    if request.user.is_authenticated:
        # Optimizacion of language selector
        language = Profile.objects.filter(user_id=request.user.id).values_list('language', flat=True).first()
        content['lan'] = language
        return content
    return content
