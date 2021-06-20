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
