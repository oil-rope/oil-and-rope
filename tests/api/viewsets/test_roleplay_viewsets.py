from model_bakery import baker
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.test import APITestCase

from roleplay.models import Campaign


class TestCampaignViewSet(APITestCase):
    url = '/api/roleplay/campaign/'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)

        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_access_logged_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_not_list_campaign_where_user_is_not_player_ok(self):
        campaign: Campaign = baker.make_recipe('roleplay.campaign')

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        results = [r['id'] for r in response.json()['results']]

        self.assertNotIn(campaign.id, results)

    def test_not_retrieve_campaign_where_user_is_not_player_ko(self):
        campaign: Campaign = baker.make_recipe('roleplay.campaign')

        url = f'{self.url}{campaign.id}/'
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(HTTP_404_NOT_FOUND, response.status_code)
