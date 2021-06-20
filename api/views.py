from django.http import JsonResponse
from django.views import View
from rest_framework import __version__ as drf_version

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
