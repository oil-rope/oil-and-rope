from django.conf import settings
from django.shortcuts import redirect


class RedirectAuthenticatedUserMixin:
    """
    This mixin redirects an authenticated user.
    """

    redirect_authenticated_user = True
    redirect_url = settings.LOGIN_REDIRECT_URL

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if self.redirect_authenticated_user and user.is_authenticated:
            return redirect(self.redirect_url)
        return super(RedirectAuthenticatedUserMixin, self).dispatch(request, *args, **kwargs)
