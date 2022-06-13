from django.apps import apps
from django.contrib.admin import ModelAdmin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from common.constants import models
from core.admin import make_private, make_public

Campaign = apps.get_model(models.ROLEPLAY_CAMPAIGN)


class TestCoreAdminFunctions(TestCase):
    dummy_model = Campaign

    @classmethod
    def setUpTestData(cls):
        class DummyModelAdmin(ModelAdmin):
            pass
        cls.modeladmin = DummyModelAdmin(cls.dummy_model, None)
        cls.qs = cls.dummy_model.objects.all()
        cls.rq = RequestFactory().get('/')

        setattr(cls.rq, 'session', 'session')
        messages = FallbackStorage(cls.rq)
        setattr(cls.rq, '_messages', messages)

    def test_make_public(self):
        make_public(self.modeladmin, self.rq, self.qs)

        self.assertEqual(self.qs.filter(is_public=False).count(), self.qs.count())

    def test_make_private(self):
        make_private(self.modeladmin, self.rq, self.qs)

        self.assertEqual(self.qs.filter(is_public=True).count(), self.qs.count())
