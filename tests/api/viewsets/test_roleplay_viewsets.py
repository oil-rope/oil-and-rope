from django.apps import apps
from django.core import mail
from django.shortcuts import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models
from common.utils import create_faker
from roleplay import baker_recipes as recipes
from roleplay.enums import RoleplaySystems

Chat = apps.get_model(models.CHAT_MODEL)
Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
PlayerInSession = apps.get_model(models.ROLEPLAY_PLAYER_IN_SESSION)
Race = apps.get_model(models.RACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)
User = apps.get_model(models.USER_MODEL)

fake = create_faker()

base_resolver = 'api:roleplay'


class TestRoleplayAPIRoot(APITestCase):

    def test_anonymous_list_urls_ok(self):
        url = reverse(f'{base_resolver}:api-root')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)


class TestDomainViewSet(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.list_url = reverse(f'{base_resolver}:domain-list')
        cls.model = Domain

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
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        # Private places
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10),
            user=self.admin_user, owner=self.admin_user
        )
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.community_places().count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_place_list_ok(self):
        self.client.force_login(self.admin_user)
        # Community places
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        # Private places
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), user=self.user, owner=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_user_places_list_ok(self):
        # Community places
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10))
        # Private places
        baker.make(_model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), user=self.user, owner=self.user)
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
        place = baker.make(self.model, owner=self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_not_owner_place_detail_ko(self):
        self.client.force_login(self.user)
        place = baker.make(self.model, owner=self.admin_user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_not_owner_place_detail_ko(self):
        self.client.force_login(self.admin_user)
        place = baker.make(self.model, owner=self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_partial_update_place_ok(self):
        place = baker.make(self.model, owner=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_ignore_user_and_owner_partial_update_place_ok(self):
        place = baker.make(self.model, owner=self.user)
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
        place = baker.make(self.model, owner=self.admin_user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_not_owner_partial_update_place_ok(self):
        place = baker.make(self.model, owner=self.user)
        self.client.force_login(self.admin_user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_owner_update_place_ko(self):
        place = baker.make(self.model, owner=self.user)
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
        place = baker.make(self.model, owner=self.user)
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
        place = baker.make(self.model, owner=self.user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_authenticated_not_admin_not_owner_delete_place_ko(self):
        place = baker.make(self.model, owner=self.admin_user)
        self.client.force_login(self.user)
        url = reverse(f'{base_resolver}:place-detail', kwargs={'pk': place.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_not_owner_delete_place_ko(self):
        place = baker.make(self.model, owner=self.user)
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


class TestSessionViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Session
        cls.list_url = reverse(f'{base_resolver}:session-list')

        cls.user = baker.make_recipe('registration.user')
        cls.admin_user = baker.make_recipe('registration.staff_user')
        cls.session_recipe = recipes.session
        cls.world = baker.make_recipe('roleplay.world')

    def test_anonymous_session_list_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_not_admin_session_list_ok(self):
        # User sessions
        self.session_recipe.make(_quantity=fake.pyint(min_value=1, max_value=10), players=[self.user])
        # Other's sessions
        self.session_recipe.make(_quantity=fake.pyint(min_value=1, max_value=10))
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.user.session_set.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_admin_session_list_ok(self):
        # User sessions
        self.session_recipe.make(_quantity=fake.pyint(min_value=1, max_value=10), players=[self.user])
        # Other's sessions
        self.session_recipe.make(_quantity=fake.pyint(min_value=1, max_value=10))
        self.client.force_login(self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_not_admin_user_in_players_retrieve_session_ok(self):
        session = self.session_recipe.make(players=[self.user])
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_not_admin_user_not_in_players_retrieve_session_ok(self):
        session = self.session_recipe.make()
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_admin_retrieve_session_ok(self):
        session = self.session_recipe.make()
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        self.client.force_login(self.admin_user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_not_admin_gm_sessions_list_ok(self):
        # User sessions
        sessions = self.session_recipe.make(_quantity=fake.pyint(min_value=1, max_value=10))
        for session in sessions:
            session.add_game_masters(self.user)
        # Other's sessions
        self.session_recipe.make(_quantity=fake.pyint(min_value=1, max_value=10))
        url = reverse(f'{base_resolver}:session-user-list')
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.user.gm_sessions.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_admin_gm_sessions_list_ok(self):
        # User sessions
        sessions = self.session_recipe.make(_quantity=fake.pyint(min_value=1, max_value=10))
        for session in sessions:
            session.add_game_masters(self.user)
        # Other's sessions
        self.session_recipe.make(_quantity=fake.pyint(min_value=1, max_value=10))
        url = reverse(f'{base_resolver}:session-user-list')
        self.client.force_login(self.admin_user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.admin_user.gm_sessions.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_not_admin_create_session_ok(self):
        self.client.force_login(self.user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'system': RoleplaySystems.PATHFINDER,
            'world': self.world.pk
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        data = response.json()
        players = data['players']
        game_masters = data['game_masters']

        self.assertIn(self.user.pk, players)
        self.assertIn(self.user.pk, game_masters)

    def test_admin_create_session_ok(self):
        self.client.force_login(self.admin_user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'system': RoleplaySystems.PATHFINDER,
            'world': self.world.pk
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        data = response.json()
        players = data['players']
        game_masters = data['game_masters']

        self.assertIn(self.admin_user.pk, players)
        self.assertIn(self.admin_user.pk, game_masters)

    def test_not_admin_game_master_update_session_ok(self):
        session = self.session_recipe.make()
        session.add_game_masters(self.user)
        self.client.force_login(self.user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'system': RoleplaySystems.PATHFINDER,
            'world': self.world.pk,
        }
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_not_admin_player_not_game_master_update_session_ok(self):
        session = self.session_recipe.make()
        self.client.force_login(self.user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'system': RoleplaySystems.PATHFINDER,
            'world': self.world.pk,
        }
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_admin_not_player_not_game_master_update_session_ok(self):
        session = self.session_recipe.make()
        self.client.force_login(self.admin_user)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'system': RoleplaySystems.PATHFINDER,
            'world': self.world.pk,
        }
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_not_admin_player_not_game_master_update_session_ko(self):
        self.client.force_login(self.user)
        session = self.session_recipe.make(players=[self.user])
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'system': RoleplaySystems.PATHFINDER,
            'world': session.world.pk,
        }
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_game_master_cannot_change_chat_ko(self):
        self.client.force_login(self.user)
        session = self.session_recipe.make()
        session.add_game_masters(self.user)
        new_chat = baker.make(Chat)
        data = {
            'chat': new_chat.pk
        }
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()['chat']
        expected_data = session.chat.pk

        self.assertEqual(expected_data, data)

    def test_admin_can_change_chat_ko(self):
        self.client.force_login(self.admin_user)
        session = self.session_recipe.make()
        new_chat = baker.make(Chat)
        data = {
            'chat': new_chat.pk
        }
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()['chat']
        expected_data = new_chat.pk

        self.assertEqual(expected_data, data)

    def test_invite_players_to_session_ok(self):
        self.client.force_login(self.user)
        session = self.session_recipe.make(players=[self.user])
        url = reverse(f'{base_resolver}:session-invite', kwargs={'pk': session.pk})
        data = {
            'players': [self.user.pk, self.admin_user.pk]
        }
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(url, data)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual(2, len(mail.outbox))
