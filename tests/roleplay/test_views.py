from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from roleplay import models


class TestWorldListView(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.model = models.Place
        self.user = baker.make(get_user_model())
        self.url = reverse('roleplay:place_list')

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/world_list.html')

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_places_are_listed_ok(self):
        entries = []
        for _ in range(0, 10):
            entries.append(
                models.Place.objects.create(name=self.faker.word(), site_type=self.model.WORLD)
            )
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        for entry in entries:
            self.assertIn(str(entry), str(response.content))

    def test_cannot_see_other_users_places_ok(self):
        another_user = baker.make(get_user_model())
        another_user_entries = []
        for _ in range(0, 10):
            another_user_entries.append(
                models.Place.objects.create(name=self.faker.country(), user=another_user, site_type=self.model.WORLD)
            )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        for entry in another_user_entries:
            self.assertNotIn(str(entry), str(response.content))

    def test_user_can_see_its_worlds_but_no_other_users_worlds_ok(self):
        another_user = baker.make(get_user_model())
        another_user_entries = []
        for _ in range(0, 10):
            another_user_entries.append(
                models.Place.objects.create(name=self.faker.name(), user=another_user, site_type=self.model.WORLD)
            )

        user_entries = []
        for _ in range(0, 10):
            user_entries.append(
                models.Place.objects.create(name=self.faker.country(), user=self.user, site_type=self.model.WORLD)
            )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        for entry in another_user_entries:
            self.assertNotIn(str(entry), str(response.content))

        for entry in user_entries:
            self.assertIn(str(entry), str(response.content))

    def test_user_can_see_community_worlds_and_its_world_but_not_other_users_worlds_ok(self):
        # To avoid repetition, we use different fakers

        another_user = baker.make(get_user_model())
        another_user_entries = []
        for _ in range(0, 10):
            another_user_entries.append(
                models.Place.objects.create(name=self.faker.name(), user=another_user, site_type=self.model.WORLD)
            )

        entries = []
        for _ in range(0, 10):
            entries.append(
                models.Place.objects.create(name=self.faker.country(), user=self.user, site_type=self.model.WORLD)
            )
            entries.append(
                models.Place.objects.create(name=self.faker.word(), site_type=self.model.WORLD)
            )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        for entry in another_user_entries:
            self.assertNotIn(str(entry), str(response.content))

        for entry in entries:
            self.assertIn(str(entry), str(response.content))
