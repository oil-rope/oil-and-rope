from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.settings import api_settings

from common.constants import models

from ..permissions import common
from ..permissions.roleplay import IsGameMasterOrAdmin, IsPlayerOrAdmin, IsPublicOrStaff
from ..serializers.roleplay import DomainSerializer, PlaceSerializer, RaceSerializer, SessionSerializer
from .mixins import StaffListAllMixin, UserListMixin

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
Race = apps.get_model(models.RACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)
User = get_user_model()


class DomainViewSet(viewsets.ModelViewSet):
    serializer_class = DomainSerializer
    queryset = Domain.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES

    def get_permissions(self):
        if self.action not in ('list', 'retrieve'):
            self.permission_classes = [IsAdminUser]
        return super(DomainViewSet, self).get_permissions()


class PlaceViewSet(UserListMixin, viewsets.ModelViewSet):
    related_name = 'places'
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [common.IsOwnerOrStaff]

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [permissions.IsAdminUser]
        if self.action == 'retrieve':
            # NOTE: Quick fix to avoid flake8 E501
            perms = api_settings.DEFAULT_PERMISSION_CLASSES + [IsPublicOrStaff | common.IsOwnerOrStaff]
            self.permission_classes = perms
        return super(PlaceViewSet, self).get_permissions()

    def get_serializer(self, *args, **kwargs):
        if 'data' not in kwargs:
            return super(PlaceViewSet, self).get_serializer(*args, **kwargs)

        user = self.request.user
        if user.is_staff:
            return super(PlaceViewSet, self).get_serializer(*args, **kwargs)

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
        return super(PlaceViewSet, self).get_serializer(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = super(PlaceViewSet, self).get_queryset()

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
        qs = super(RaceViewSet, self).get_queryset()

        if self.action == 'user_list':
            return qs

        if not user.is_staff:
            qs = user.race_set.all()

        return qs


class SessionViewSet(StaffListAllMixin, UserListMixin, viewsets.ModelViewSet):
    related_name = 'gm_sessions'
    queryset = Session.objects.all()
    permission_classes = [IsAuthenticated & IsPlayerOrAdmin]
    serializer_class = SessionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # NOTE: Staff user needs to have access to all sessions that are not specific user lists
        if self.request.user.is_staff and self.action not in ('user_list', 'list'):
            return qs
        return qs.filter(
            players__in=[self.request.user]
        )

    def get_permissions(self):
        if self.action in ('partial_update', 'update', 'destroy'):
            self.permission_classes = [IsGameMasterOrAdmin]
        return super(SessionViewSet, self).get_permissions()

    def perform_create(self, serializer):
        obj = serializer.save()
        obj.add_game_masters(self.request.user)
        return obj
