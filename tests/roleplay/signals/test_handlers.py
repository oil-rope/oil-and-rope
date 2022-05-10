import random

from django.apps import apps
from django.test import TestCase
from model_bakery import baker

from common.constants import models
from roleplay.enums import RoleplaySystems
from tests import fake

Campaign = apps.get_model(models.ROLEPLAY_CAMPAIGN)


class TestCampaignPreSave(TestCase):
    model = Campaign

    @classmethod
    def setUpTestData(cls):
        cls.owner = baker.make_recipe('registration.user')
        cls.world = baker.make_recipe('roleplay.world')

    def setUp(self):
        self.data_ok = {
            'name': fake.sentence(),
            'system': random.choice(RoleplaySystems.values),
            'owner': self.owner,
            'place': self.world,
        }

    def test_chat_is_assigned_automatically_ok(self):
        campaign = self.model.objects.create(**self.data_ok)

        self.assertIsNotNone(campaign.chat)
