from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.detail import SingleObjectMixin


class UserInAllWithRelatedNameMixin(SingleObjectMixin, UserPassesTestMixin):
    """
    This mixin checks if the user is in `all()` queryset using a related_name attribute on an object got by
    `self.get_object()`.
    """

    related_name_attr = 'users'

    def test_func(self):
        if not self.related_name_attr:
            raise NotImplementedError('UserIsPlayerMixin requires a definition of \'related_name_attr\'.')

        # Getting the object
        obj = self.get_object()
        # Checking if object has related_name_attr
        if not hasattr(obj, self.related_name_attr):
            raise ImproperlyConfigured('Object does not have \'related_name_attr\'.')
        # Checking if user is in players
        if self.request.user in getattr(obj, self.related_name_attr).all():
            return True

        return False
