import functools
from typing import TYPE_CHECKING

from django.apps import apps
from django.test import TestCase
from model_bakery import baker

from common.constants import models as constants
from roleplay.enums import DomainTypes, SiteTypes
from tests.utils import fake, generate_place

if TYPE_CHECKING:
    from django.contrib.contenttypes.models import ContentType as ContentTypeModel

    from common.models import Vote as VoteModel
    from roleplay.models import Campaign as CampaignModel
    from roleplay.models import Domain as DomainModel
    from roleplay.models import Place as PlaceModel

Campaign: 'CampaignModel' = apps.get_model(constants.ROLEPLAY_CAMPAIGN)
ContentType: 'ContentTypeModel' = apps.get_model(constants.CONTENT_TYPE)
Domain: 'DomainModel' = apps.get_model(constants.ROLEPLAY_DOMAIN)
Place: 'PlaceModel' = apps.get_model(constants.ROLEPLAY_PLACE)
Vote: 'VoteModel' = apps.get_model(constants.COMMON_VOTE)


class TestDomainManager(TestCase):
    model = Domain

    def setUp(self):
        self.number_of_domains = fake.pyint(min_value=1, max_value=100)
        baker.make(self.model, self.number_of_domains, domain_type=DomainTypes.DOMAIN)
        self.number_of_subdomains = fake.pyint(min_value=1, max_value=100)
        baker.make(self.model, self.number_of_subdomains, domain_type=DomainTypes.SUBDOMAIN)

    def test_all_ok(self):
        total = self.number_of_domains + self.number_of_subdomains
        self.assertEqual(total, self.model.objects.count())

    def test_domains_ok(self):
        self.assertEqual(self.number_of_domains, self.model.objects.domains().count())

    def test_subdomains_ok(self):
        self.assertEqual(self.number_of_subdomains, self.model.objects.subdomains().count())


class TestCampaignManager(TestCase):
    model = Campaign

    @classmethod
    def setUpTestData(cls):
        cls.content_type = ContentType.objects.get_for_model(cls.model)
        cls.campaign_with_votes = baker.make_recipe('roleplay.campaign')
        baker.make(Vote, content_type=cls.content_type, object_id=cls.campaign_with_votes.pk)

    def test_campaign_is_returned_with_votes_ok(self):
        campaign = self.model.objects.with_votes().first()

        self.assertTrue(hasattr(campaign, 'positive_votes'))
        self.assertTrue(hasattr(campaign, 'negative_votes'))
        self.assertTrue(hasattr(campaign, 'total_votes'))


class TestPlaceManager(TestCase):
    enum = SiteTypes
    model = Place

    def setUp(self):
        self.user = baker.make_recipe('registration.user')
        random_int = functools.partial(fake.pyint, min_value=1, max_value=100)

        self.number_of_worlds = random_int()
        generate_place(self.number_of_worlds, site_type=self.enum.WORLD, is_public=True)

        self.total = self.number_of_worlds

    def test_community_places(self):
        expected_queries = 1
        with self.assertNumQueries(expected_queries):
            result = self.model.objects.community_places()
            self.assertEqual(self.total, result.count())

    def test_worlds_ok(self):
        self.assertEqual(self.number_of_worlds, self.model.objects.worlds().count())
