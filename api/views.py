from django.shortcuts import resolve_url
from django.urls import NoReverseMatch
from django.utils.translation import gettext_lazy as _
from rest_framework import __title__ as drf_title
from rest_framework import __version__ as drf_version
from rest_framework import permissions, status, views
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from core.exceptions import OilAndRopeException
from roleplay.utils.dice import roll_dice

from . import get_version


class ApiVersionView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        data = {
            'version': get_version(),
            'powered_by': drf_title,
            'drf_version': drf_version,
            'using_version': request.version or _('not versioning supported').capitalize(),
        }
        return Response(data=data, status=status.HTTP_200_OK)


class URLResolverView(views.APIView):
    """
    Returns URL with given resolver and params.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        data = request.data.copy()
        if 'resolver' not in data:
            raise ValidationError()

        resolver = data.pop('resolver')
        if isinstance(resolver, list):
            resolver = resolver[0]
        extra_params = {}
        for key, value in data.items():
            extra_params[key] = value

        try:
            url = resolve_url(resolver, **extra_params)
        except NoReverseMatch:
            url = '#no-url'

        data = {'url': url}
        return Response(data=data, status=status.HTTP_200_OK)


class RollView(views.APIView):
    """
    Rolls a dice and returns results.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        if 'roll' not in request.data:
            msg = _('\'roll\' field is required.')
            raise ValidationError(msg)

        try:
            result, rolls = roll_dice(request.data['roll'])
            data = {'result': result, 'rolls': rolls}
            return Response(data=data, status=status.HTTP_200_OK)
        except OilAndRopeException as ex:
            raise ValidationError(ex.message)
