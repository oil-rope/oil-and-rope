from django.shortcuts import resolve_url
from django.urls import NoReverseMatch
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import __title__ as drf_title
from rest_framework import __version__ as drf_version
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from core.exceptions import OilAndRopeException
from roleplay.utils.dice import roll_dice

from .. import get_version
from ..serializers import api as serializers


class ApiVersionView(GenericAPIView):
    pagination_class = None
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ApiVersionSerializer

    # NOTE: Overriding to get typing notations
    def get_serializer(self, *args, **kwargs) -> serializers.ApiVersionSerializer:
        return super().get_serializer(*args, **kwargs)

    @swagger_auto_schema(
        tags=['utils'],
        operation_summary='Get API information',
        operation_id='api:info',
    )
    def get(self, request: Request) -> Response:
        """
        Returns the API version among other information.
        """

        serializer = self.get_serializer(
            data={
                'version': get_version(),
                'powered_by': drf_title,
                'drf_version': drf_version,
                'using_version': request.version or _('not versioning supported').capitalize(),
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class URLResolverView(GenericAPIView):
    pagination_class = None
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.URLResolverSerializer

    # NOTE: Overriding to get typing notations
    def get_serializer(self, *args, **kwargs) -> serializers.URLResolverSerializer:
        return super().get_serializer(*args, **kwargs)

    @swagger_auto_schema(
        tags=['utils'],
        operation_summary='Get URL from resolver',
        operation_id='api:resolver',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Successful Response',
                schema=serializers.URLResolverResponseSerializer,
            ),
        }
    )
    def post(self, request: Request) -> Response:
        """
        Returns URL with given resolver and params.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resolver = serializer.data['resolver']
        params = serializer.data.get('params', {})

        try:
            url = resolve_url(resolver, **params)
        except NoReverseMatch:
            url = '#no-url'

        response_serializer = serializers.URLResolverResponseSerializer(data={'url': url})
        response_serializer.is_valid(raise_exception=True)

        return Response(data=response_serializer.data, status=status.HTTP_200_OK)


class RollView(GenericAPIView):
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.DiceRollSerializer

    # NOTE: Overriding to get typing notations
    def get_serializer(self, *args, **kwargs) -> serializers.DiceRollSerializer:
        return super().get_serializer(*args, **kwargs)

    @swagger_auto_schema(
        tags=['roleplay', 'utils'],
        operation_summary='Roll dice',
        operation_id='roleplay:roll',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Successful Response',
                schema=serializers.DiceRollResponseSerializer,
                examples={
                    'application/json': {
                        'result': '19',
                        'rolls': {
                            'd20': [15],
                            '+2d4': [1, 3],
                        },
                    }
                }
            )
        }
    )
    def post(self, request: Request) -> Response:
        """
        From given dice string, rolls dice and returns results.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result, rolls = roll_dice(serializer.data['roll'])
            response_serializer = serializers.DiceRollResponseSerializer(data={'result': result, 'rolls': rolls})
            response_serializer.is_valid(raise_exception=True)
            return Response(data=response_serializer.data, status=status.HTTP_200_OK)
        except OilAndRopeException as ex:
            raise ValidationError(ex.message)
