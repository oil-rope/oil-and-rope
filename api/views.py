from django.http import JsonResponse
from django.shortcuts import reverse
from django.urls import NoReverseMatch
from django.views import View
from rest_framework import __version__ as drf_version
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from oilandrope import __version__


class ApiVersionView(View):
    http_method_names = ['get']
    data = {
        'version': __version__,
        'powered_by': 'Django Rest Framework',
        'drf_version': drf_version,
    }

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.data)


class URLResolverViewSet(ViewSet):
    """
    Returns URL with given resolver and params.
    """

    permission_classes = [AllowAny]

    def resolve_url(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'resolver' not in data:
            raise ValidationError()

        resolver = data.pop('resolver')
        if isinstance(resolver, list):
            resolver = resolver[0]
        extra_params = {}
        for key,  value in data.items():
            extra_params[key] = value

        try:
            url = reverse(resolver, kwargs=extra_params)
        except NoReverseMatch:
            url = '#no-url'

        return Response({'url': url})
