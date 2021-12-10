from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import View


class StaffRequiredMixin(View):
    """
    Checks if user is staff.
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated or not user.is_staff:
            msg = _('you are trying to access an Staff page but you are not staff')
            messages.warning(request, f'{msg}.')
            return redirect(to=settings.LOGIN_URL)

        return super().dispatch(request, *args, **kwargs)
