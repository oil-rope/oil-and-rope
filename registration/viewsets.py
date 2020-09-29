from django.contrib.auth import get_user_model
from rest_framework import viewsets

from .models import Profile
from .permissions import IsModelOwner
from .serializers import ProfileSerializer, UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`User`.
    """

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsModelOwner]


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`Profile`.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsModelOwner]
