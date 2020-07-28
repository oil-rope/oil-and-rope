import json
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import reverse


class ResolverView(View):
    """
    This view returns the URL by a give resolver as `url_resolver` data.
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        try:
            url_resolver = data.get('url_resolver', '')
            json_data = {'url': reverse(url_resolver)}
        except Exception:
            json_data = {'url': '#no-url'}

        return JsonResponse(data=json_data)
