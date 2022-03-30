from django.core.exceptions import ImproperlyConfigured
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser


class UserListMixin:
    """
    Returns a queryset by a given reverse relation.
    """

    related_name = None

    def get_related_name(self):
        if not self.related_name:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} should either include a `related_name` attribute, \
                  or override the `get_related_name` method.'
            )
        return self.related_name

    def get_reverse_relation(self):
        user = self.request.user
        related_name = self.get_related_name()
        if not hasattr(user, related_name):
            raise AttributeError(f'User doesn\'t have {related_name} attribute.')
        return getattr(user, related_name)

    def get_queryset(self):
        if self.action == 'user_list':
            return self.get_reverse_relation().all()
        return super().get_queryset()

    @action(methods=['get'], detail=False, url_path='@me', url_name='user-list')
    def user_list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class StaffListAllMixin:
    """
    If user is staff is a allowed to see all the objects.
    """

    def get_queryset(self):
        if self.action == 'list_all':
            return super().get_queryset().model.objects.all()
        return super().get_queryset()

    @action(methods=['get'], detail=False, url_path='all', url_name='list-all', permission_classes=[IsAdminUser])
    def list_all(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
