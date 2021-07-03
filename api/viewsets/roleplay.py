from django.apps import apps
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.settings import api_settings

from common.constants import models

from ..permissions import common
from ..permissions.roleplay import IsInGameMastersOrStaff, IsInPlayersOrStaff
from ..serializers.roleplay import DomainSerializer, PlaceSerializer, RaceSerializer, SessionSerializer
from .mixins import UserListMixin

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
Race = apps.get_model(models.RACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)


class DomainViewSet(viewsets.ModelViewSet):
    serializer_class = DomainSerializer
    queryset = Domain.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES

    def get_permissions(self):
        if self.action not in ('list', 'retrieve'):
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class PlaceViewSet(UserListMixin, viewsets.ModelViewSet):
    related_name = 'places'
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [common.IsOwnerOrStaff]

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        if 'data' not in kwargs:
            return super().get_serializer(*args, **kwargs)

        user = self.request.user
        if user.is_staff:
            return super().get_serializer(*args, **kwargs)

        data = kwargs['data'].copy()

        if self.action == 'partial_update':
            if 'owner' in data:
                del data['owner']
            if 'user' in data:
                del data['user']

        if self.action == 'create':
            data.appendlist('owner', user.pk)
            if not data.get('public', False):
                data.appendlist('user', user.pk)

        kwargs['data'] = data
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if self.action == 'list' and not user.is_staff:
            qs = Place.objects.community_places()

        return qs


class RaceViewSet(UserListMixin, viewsets.ModelViewSet):
    related_name = 'owned_races'
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [common.IsInOwnersOrStaff]
    queryset = Race.objects.all()
    serializer_class = RaceSerializer

    def perform_create(self, serializer):
        """
        We add the user that performed create to owners.
        """

        obj = serializer.save()
        user = self.request.user
        obj.add_owners(user)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if self.action == 'user_list':
            return qs

        if not user.is_staff:
            qs = user.race_set.all()

        return qs


class SessionViewSet(UserListMixin, viewsets.ModelViewSet):
    related_name = 'gm_sessions'
    queryset = Session.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsInPlayersOrStaff]
    serializer_class = SessionSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action == 'user_list':
            return qs

        user = self.request.user
        if not user.is_staff:
            qs = user.session_set.all()

        return qs

    def get_serializer(self, *args, **kwargs):
        user = self.request.user
        if user.is_staff:
            return super().get_serializer(*args, **kwargs)

        if self.action in ('list', 'user_list', 'retrieve', 'create'):
            return super().get_serializer(*args, **kwargs)

        data = kwargs['data'].copy()

        if 'chat' in data:
            del data['chat']

        kwargs['data'] = data

        return super().get_serializer(*args, **kwargs)

    def get_permissions(self):
        if self.action in ('partial_update', 'update'):
            self.permission_classes = [IsInGameMastersOrStaff]
        return super().get_permissions()

    def perform_create(self, serializer):
        obj = serializer.save()
        user = self.request.user
        obj.add_game_masters(user)
        return obj
