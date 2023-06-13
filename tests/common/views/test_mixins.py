from typing import Any

from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase
from django.views.generic.detail import BaseDetailView
from model_bakery import baker

from common.views.mixins import ImageFormsetMixin
from roleplay.models import Race
from tests.utils import fake


class TestImageFormsetMixin(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.factory = RequestFactory()
        cls.object = baker.make_recipe('roleplay.race')

    def setUp(self) -> None:
        class DummyView(ImageFormsetMixin, BaseDetailView):
            model = Race

            def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
                # From BaseDetailView
                return super().get(request, *args, **kwargs)

            def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
                return super().get(request, *args, **kwargs)

            def render_to_response(self, context):
                content = """
                Works!
                <form method="POST" action="/" id="%(form_prefix)s"></form>
                """ % {'form_prefix': self.get_image_formset_prefix()}
                response = HttpResponse(content=content.encode())
                response.context = context
                return response

        self.View = DummyView

    def test_image_formset_is_added_to_the_context_on_get_ok(self):
        request = self.factory.get('/')
        request.user = baker.make_recipe('registration.user')

        response = self.View.as_view()(request, pk=self.object.pk)

        self.assertIn('image_formset', response.context)

    def test_image_formset_is_added_to_the_context_on_put_ok(self):
        request = self.factory.post('/', data={})
        request.user = baker.make_recipe('registration.user')

        response = self.View.as_view()(request, pk=self.object.pk)

        self.assertIn('image_formset', response.context)

    def test_image_formset_is_added_to_the_context_on_post_ok(self):
        request = self.factory.post('/', data={})
        request.user = baker.make_recipe('registration.user')

        response = self.View.as_view()(request, pk=self.object.pk)

        self.assertIn('image_formset', response.context)

    def test_image_formset_prefix_is_given_and_used_ok(self):
        formset_prefix = fake.word()
        self.View.image_formset_prefix = formset_prefix

        request = self.factory.get('/')
        request.user = baker.make_recipe('registration.user')

        response = self.View.as_view()(request, pk=self.object.pk)

        self.assertIn(formset_prefix, response.content.decode())
