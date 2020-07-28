from django.http import JsonResponse
from django.shortcuts import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic import View


class ResolverView(View):
    """
    This view returns the URL by a give resolver as `url_resolver` data.
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        data = request.POST

        try:
            url_resolver = data.get('url_resolver', '')
            json_data = {'url': reverse(url_resolver)}
        except NoReverseMatch:
            json_data = {'url': '#no-url'}

        return JsonResponse(data=json_data)
