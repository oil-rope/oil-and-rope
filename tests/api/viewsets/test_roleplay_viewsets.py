from django.apps import apps
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models
from common.utils import create_faker
from roleplay import baker_recipes as recipes
from tests.api.viewsets.utils import bake_places

Chat = apps.get_model(models.CHAT)
Domain = apps.get_model(models.ROLEPLAY_DOMAIN)
Place = apps.get_model(models.ROLEPLAY_PLACE)
Race = apps.get_model(models.ROLEPLAY_RACE)
User = get_user_model()

fake = create_faker()

base_resolver = 'api:roleplay'


class TestDomainViewSet(APITestCase):
    list_url = reverse(f'{base_resolver}:domain-list')
    model = Domain

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.admin_user = baker.make_recipe('registration.staff_user')
        cls.domain_recipe = recipes.domain

    def test_anonymous_domain_list_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_domain_list_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_domain_list_ok(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_domain_detail_ok(self):
        self.client.force_login(self.user)
        domain = self.domain_recipe.make()
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_domain_detail_ok(self):
        self.client.force_login(self.admin_user)
        domain = self.domain_recipe.make()
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_create_ko(self):
        self.client.force_login(self.user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_create_ok(self):
        self.client.force_login(self.admin_user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_authenticated_not_admin_partial_update_ko(self):
        self.client.force_login(self.user)
        domain = self.domain_recipe.make()
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_partial_update_ok(self):
        self.client.force_login(self.admin_user)
        domain = self.domain_recipe.make()
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_update_ko(self):
        self.client.force_login(self.user)
        domain = self.domain_recipe.make()
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_update_ok(self):
        self.client.force_login(self.admin_user)
        domain = self.domain_recipe.make()
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_delete_ko(self):
        self.client.force_login(self.user)
        domain = self.domain_recipe.make()
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_delete_ok(self):
        self.client.force_login(self.admin_user)
        domain = self.domain_recipe.make()
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class TestPlaceViewSet(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.model = Place
        cls.list_url = reverse(f'{base_resolver}:place-list')

        cls.user = baker.make_recipe('registration.user')
        cls.admin_user = baker.make_recipe('registration.staff_user')

    def test_anonymous_place_list_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_community_places_list_ok(self):
        self.client.force_login(self.user)
        # Community places
        bake_places()
        # Private places
        bake_places(user=self.admin_user, owner=self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.community_places().count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_place_list_ok(self):
        self.client.force_login(self.admin_user)
        # Community places
        bake_places()
        # Private places
        bake_places(user=self.user, owner=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_user_places_list_ok(self):
        # Community places
        bake_places()
        # Private places
        bake_places(user=self.user, owner=self.user)
        # Different user's private places
        another_user = baker.make(User)
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), user=another_user, owner=another_user
        )
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-user-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.user.places.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_not_admin_owner_place_detail_ok(self):
        self.client.force_login(self.user)
        place = bake_places(_quantity=1, owner=self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_not_owner_place_detail_ko(self):
        self.client.force_login(self.user)
        place = bake_places(_quantity=1, owner=self.admin_user, user=self.admin_user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_not_owner_place_detail_ko(self):
        self.client.force_login(self.admin_user)
        place = bake_places(_quantity=1, owner=self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_partial_update_place_ok(self):
        place = bake_places(_quantity=1, owner=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_ignore_user_and_owner_partial_update_place_ok(self):
        place = bake_places(_quantity=1, owner=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'owner': self.admin_user.pk,
            'user': self.admin_user.pk,
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.user.pk
        data = self.client.get(url).json()

        self.assertEqual(expected_data, data['owner'])

    def test_authenticated_not_admin_not_owner_partial_update_place_ko(self):
        place = bake_places(_quantity=1, owner=self.admin_user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_not_owner_partial_update_place_ok(self):
        place = bake_places(_quantity=1, owner=self.user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_update_place_ko(self):
        place = bake_places(_quantity=1, owner=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'owner': self.user,
            'user': self.user,
        }
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_not_owner_update_place_ok(self):
        place = bake_places(_quantity=1, owner=self.user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'owner': self.user.pk,
            'user': self.user.pk,
        }
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_delete_place_ok(self):
        place = bake_places(_quantity=1, owner=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_authenticated_not_admin_not_owner_delete_place_ko(self):
        place = bake_places(_quantity=1, owner=self.admin_user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_not_owner_delete_place_ko(self):
        place = bake_places(_quantity=1, owner=self.user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_authenticated_not_admin_create_private_place_ok(self):
        self.client.force_login(self.user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': response.json()['id']})
        data = self.client.get(url).json()

        self.assertEqual(data['user'], self.user.pk)

    def test_authenticated_not_admin_create_public_place_ok(self):
        self.client.force_login(self.user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'public': True,
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': response.json()['id']})
        data = self.client.get(url).json()

        self.assertIsNone(data['user'])

    def test_authenticated_admin_create_place_ok(self):
        self.client.force_login(self.admin_user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'owner': self.user.pk,
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        expected_data = self.user.pk
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': response.json()['id']})
        data = self.client.get(url).json()

        self.assertEqual(expected_data, data['owner'])


class TestRaceViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Race
        cls.list_url = reverse(f'{base_resolver}:race-list')

        cls.user = baker.make_recipe('registration.user')
        cls.admin_user = baker.make_recipe('registration.staff_user')

    def test_anonymous_race_list_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_race_list_ok(self):
        self.client.force_login(self.user)
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        race = baker.make(self.model)
        race.add_owners(self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.user.race_set.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_race_list_ok(self):
        self.client.force_login(self.admin_user)
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_not_admin_owned_races_list_ok(self):
        self.client.force_login(self.user)
        # Not owned races
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        # Owned race
        race = baker.make(self.model)
        race.add_owners(self.user)
        url = reverse(f'{base_resolver}:race-user-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.user.owned_races.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_owned_races_list_ok(self):
        self.client.force_login(self.admin_user)
        # Not owned races
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        # Owned race
        race = baker.make(self.model)
        race.add_owners(self.admin_user)
        url = reverse(f'{base_resolver}:race-user-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.admin_user.owned_races.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_not_admin_owner_race_detail_ok(self):
        self.client.force_login(self.user)
        race = baker.make(self.model)
        race.add_owners(self.user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_not_owner_race_detail_ok(self):
        self.client.force_login(self.user)
        race = baker.make(self.model)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_admin_owner_race_detail_ok(self):
        self.client.force_login(self.admin_user)
        race = baker.make(self.model)
        race.add_owners(self.admin_user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_not_owner_race_detail_ok(self):
        self.client.force_login(self.admin_user)
        race = baker.make(self.model)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_race_update_ok(self):
        self.client.force_login(self.user)
        race = baker.make(self.model)
        race.add_owners(self.user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_not_owner_race_update_ok(self):
        self.client.force_login(self.user)
        race = baker.make(self.model)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_admin_owner_race_update_ok(self):
        self.client.force_login(self.admin_user)
        race = baker.make(self.model)
        race.add_owners(self.admin_user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_not_owner_race_update_ok(self):
        self.client.force_login(self.admin_user)
        race = baker.make(self.model)
        race.add_owners(self.user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_race_partial_update_ok(self):
        self.client.force_login(self.user)
        race = baker.make(self.model)
        race.add_owners(self.user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        data = {
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_not_owner_race_partial_update_ok(self):
        self.client.force_login(self.user)
        race = baker.make(self.model)
        race.add_owners(self.admin_user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        data = {
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_admin_owner_race_partial_update_ok(self):
        self.client.force_login(self.admin_user)
        race = baker.make(self.model)
        race.add_owners(self.admin_user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        data = {
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_not_owner_race_partial_update_ok(self):
        self.client.force_login(self.admin_user)
        race = baker.make(self.model)
        race.add_owners(self.user)
        url = reverse(f'{base_resolver}:race-detail', kwargs={'pk': race.pk})
        data = {
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_race_create_ok(self):
        self.client.force_login(self.user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        race = self.model.objects.get(pk=response.json()['id'])

        self.assertIn(self.user, race.owners)

    def test_authenticated_admin_race_create_ok(self):
        self.client.force_login(self.admin_user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        race = self.model.objects.get(pk=response.json()['id'])

        self.assertIn(self.admin_user, race.owners)
