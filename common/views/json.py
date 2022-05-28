from distutils.util import strtobool as to_bool

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, resolve_url
from django.urls.exceptions import NoReverseMatch
from django.views.generic import View

from common.constants import models as constants

ContentType = apps.get_model(constants.CONTENT_TYPE)
Vote = apps.get_model(constants.COMMON_VOTE)


class ResolverView(View):
    """
    This view returns the URL by a give resolver as `url_resolver` data.
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        data = request.POST

        try:
            url_resolver = data.get('url_resolver', '')
            json_data = {'url': resolve_url(url_resolver)}
        except NoReverseMatch:
            json_data = {'url': '#no-url'}

        return JsonResponse(data=json_data)


class VoteView(LoginRequiredMixin, View):
    """
    This view will add a vote for a given model and instance ID.
    """

    http_method_names = ['get']

    def get_content_type(self):
        app_label, model = self.kwargs['model'].split('.')
        return get_object_or_404(
            ContentType,
            app_label=app_label,
            model=model,
        )

    def get_object(self):
        content_type = self.get_content_type()
        return get_object_or_404(
            content_type.model_class(),
            pk=self.kwargs['pk'],
        )

    def get_vote(self):
        self.object = self.get_object()
        obj, created = Vote.objects.get_or_create(
            user=self.request.user,
            content_type=self.get_content_type(),
            object_id=self.object.pk,
        )
        if not created:
            obj.is_positive = to_bool(self.request.GET.get('is_positive', 'false'))
            obj.save(update_fields=['is_positive'])
        return obj

    def get(self, *args, **kwargs):
        vote = self.get_vote()
        return JsonResponse(data={'id': vote.id})
