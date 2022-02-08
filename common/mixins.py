from django.core.exceptions import ImproperlyConfigured, PermissionDenied


class OwnerRequiredMixin:
    """
    Checks if user is owner by :class:`owner_attribute`.
    """

    owner_attr = 'owner'

    def dispatch(self, request, *args, **kwargs):
        # If user is not authenticated keep on
        if not self.request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if not self.owner_attr:
            raise ImproperlyConfigured('OwnerRequiredMixin requires a definition of \'owner_attr\'.')

        # Checking for owner
        obj = self.get_object()
        if self.request.user != getattr(obj, self.owner_attr):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
