from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin


class OwnerRequiredMixin(SingleObjectMixin, View):
    """
    Checks if user is owner by :class:`owner_attribute`.
    """

    owner_attr = 'owner'

    def dispatch(self, request, *args, **kwargs):
        # If user is not authenticated keep on
        if not self.request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        # Checking for owner
        obj = self.get_object()
        if not hasattr(obj, self.owner_attr):
            return
        if self.request.user == getattr(obj, self.owner_attr):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied
