from django.apps import apps
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from common.admin import VoteAdmin
from common.constants import models

Vote = apps.get_model(models.COMMON_VOTE)


class TestVoteAdmin(TestCase):
    model = Vote
    model_admin_class = VoteAdmin

    @classmethod
    def setUpTestData(cls):
        cls.model_admin = cls.model_admin_class(cls.model, None)
        cls.qs = cls.model.objects.all()
        cls.rq = RequestFactory().get('/')

        setattr(cls.rq, 'session', 'session')
        messages = FallbackStorage(cls.rq)
        setattr(cls.rq, '_messages', messages)

    def test_make_positive(self):
        self.model_admin.make_positive(self.rq, self.qs)

        self.assertEqual(self.qs.filter(is_positive=True).count(), self.qs.count())

    def test_make_negative(self):
        self.model_admin.make_negative(self.rq, self.qs)

        self.assertEqual(self.qs.filter(is_positive=False).count(), self.qs.count())
