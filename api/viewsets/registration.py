from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from registration.models import User

from ..serializers.registration import BotSerializer, UserSerializer


class UserViewSet(APIView):
    queryset = User.objects.none()
    serializer_class = UserSerializer

    @extend_schema(
        operation_id='api:registration:user',
        summary='Get user',
    )
    def get(self, request: Request):
        """
        Gets logged user and returns it as a JSON object.
        """

        return Response(data=self.serializer_class(request.user).data, status=status.HTTP_200_OK)


class BotViewSet(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BotSerializer

    @extend_schema(
        operation_id='api:registration:bot',
        summary='Get Oil & Rope Bot',
    )
    def get(self, _) -> Response:
        """
        Gets Oil & Rope Bot and returns it as a JSON object.
        """

        bot = User.objects.get(email=settings.DEFAULT_FROM_EMAIL)
        serializer = self.serializer_class(bot)
        return Response(data=serializer.data)
