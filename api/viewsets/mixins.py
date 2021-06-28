from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response


class ListStaffRequiredMixin(ListModelMixin):
    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_staff or user.is_superuser:
            return super().list(request, *args, **kwargs)
        else:
            msg = _('You don\'t have permission to perform this action')
            return Response(data=f'{msg}.', status=status.HTTP_403_FORBIDDEN)


# noinspection PyUnresolvedReferences
class UserListMixin:
    """
    Returns a queryset by a given reverse relation.
    """

    related_name = None

    def get_related_name(self):
        if not self.related_name:
            raise ImproperlyConfigured(
                _('%(class_name)s should either include a `related_name` attribute, \
                  or override the `get_related_name` method.') % {
                    'class_name': self.__class__.__name__
                }
            )
        return self.related_name

    def get_reverse_relation(self):
        user = self.request.user
        if not hasattr(user, self.related_name):
            raise AttributeError(
                _('User doesn\'t have %(related_name)s attribute.') % {
                    'related_name': self.get_related_name()
                }
            )
        return getattr(user, self.related_name)

    def get_queryset(self):
        if self.action == 'user_list':
            return self.get_reverse_relation().all()
        return super().get_queryset()

    def user_list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
