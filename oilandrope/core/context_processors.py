from django.conf import settings
from registration.models import Profile


def language(request):
    """
    Sets language depending on the profile.
    """

    if request.user.is_authenticated:
        profile = Profile.objects.get_or_create(user=request.user)[0]
        return {'lan': profile.language}
    return {'lan': settings.LANGUAGE_CODE}
