from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured


class OwnerRequiredMixin(UserPassesTestMixin):
    """
    Checks if user is owner by :class:`owner_attribute`.
    """

    owner_attr = 'owner'

    def test_func(self):
        if not self.owner_attr:
            raise ImproperlyConfigured('OwnerRequiredMixin requires a definition of \'owner_attr\'.')

        # Checking for owner
        self.object = self.get_object()
        if self.request.user == getattr(self.object, self.owner_attr):
            return True

        return False
