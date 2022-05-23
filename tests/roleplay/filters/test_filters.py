from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from roleplay import filters


class TestCampaignFilter(TestCase):
    filter_class = filters.CampaignFilter

    def test_get_active_true_with_end_date_in_past_campaign_is_not_listed(self):
        campaign = baker.make_recipe('roleplay.campaign', end_date=timezone.now() - timezone.timedelta(days=1))
        qs = self.filter_class(data={'active': True}).qs

        self.assertNotIn(campaign, qs)

    def test_get_active_false_with_end_date_in_past_campaign_is_listed(self):
        campaign = baker.make_recipe('roleplay.campaign', end_date=timezone.now() - timezone.timedelta(days=1))
        qs = self.filter_class(data={'active': False}).qs

        self.assertIn(campaign, qs)
