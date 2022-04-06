import random

from django.apps import apps
from django.shortcuts import resolve_url, reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from common.constants import models
from common.utils import create_faker
from roleplay import baker_recipes as recipes
from roleplay.enums import RoleplaySystems
from tests.api.viewsets.utils import bake_places

Chat = apps.get_model(models.CHAT_MODEL)
Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
PlayerInSession = apps.get_model(models.ROLEPLAY_PLAYER_IN_SESSION)
Race = apps.get_model(models.RACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)
User = apps.get_model(models.USER_MODEL)

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


class TestSessionViewSet(APITestCase):
    model = Session
    list_url = resolve_url(f'{base_resolver}:session-list')

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.user_token = Token.objects.create(user=cls.user)
        cls.user_credentials = {
            'HTTP_AUTHORIZATION': f'Token {cls.user_token.key}',
        }

        cls.staff_user = baker.make_recipe('registration.staff_user')
        cls.staff_user_token = Token.objects.create(user=cls.staff_user)
        cls.staff_user_credentials = {
            'HTTP_AUTHORIZATION': f'Token {cls.staff_user_token.key}',
        }

        cls.world = baker.make_recipe('roleplay.world')

    def setUp(self):
        self.data_ok = {
            'name': fake.sentence(),
            'plot': fake.paragraph(),
            'world': self.world.pk,
            'system': random.choice(RoleplaySystems.values),
        }

    def test_anonymous_session_list_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_list_ok(self):
        self.client.credentials(**self.user_credentials)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_list_length_ok(self):
        # User sessions
        session_instances = baker.make_recipe('roleplay.session', _quantity=5, players=[self.user])
        # Sessions where user is not in players
        baker.make_recipe('roleplay.session', _quantity=5)
        self.client.credentials(**self.user_credentials)
        response = self.client.get(self.list_url)

        self.assertEqual(len(session_instances), len(response.json()['results']))

    def test_authenticated_admin_list_ok(self):
        self.client.credentials(**self.staff_user_credentials)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_staff_list_length_ok(self):
        # Admin sessions
        session_instances = baker.make_recipe('roleplay.session', _quantity=5, players=[self.staff_user])
        # Sessions where staff is not in players
        baker.make_recipe('roleplay.session', _quantity=5)
        self.client.credentials(**self.staff_user_credentials)
        response = self.client.get(self.list_url)

        self.assertEqual(len(session_instances), len(response.json()['results']))

    def test_anonymous_session_retrieve_ko(self):
        session = baker.make_recipe('roleplay.session')
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_in_players_retrieve_ok(self):
        session = baker.make_recipe('roleplay.session', players=[self.user])
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_not_in_players_retrieve_ko(self):
        session = baker.make_recipe('roleplay.session')
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        self.client.credentials(**self.user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_staff_retrieve_ok(self):
        session = baker.make_recipe('roleplay.session')
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        self.client.credentials(**self.staff_user_credentials)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_anonymous_session_create_ko(self):
        response = self.client.post(self.list_url, self.data_ok, format='json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_session_create_ok(self):
        self.client.credentials(**self.user_credentials)
        response = self.client.post(self.list_url, self.data_ok, format='json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_authenticated_user_session_is_created_and_user_added_to_game_masters_ok(self):
        self.client.credentials(**self.user_credentials)
        response = self.client.post(self.list_url, self.data_ok, format='json')

        self.assertIn(self.user.pk, response.json()['game_masters'])

    def test_authenticated_staff_session_create_ok(self):
        self.client.credentials(**self.staff_user_credentials)
        response = self.client.post(self.list_url, self.data_ok, format='json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_authenticated_user_game_master_session_partial_update_ok(self):
        self.client.credentials(**self.user_credentials)
        session = baker.make_recipe('roleplay.session')
        session.add_game_masters(self.user)
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        data = {
            'name': fake.sentence(),
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_not_game_master_session_partial_update_ko(self):
        self.client.credentials(**self.user_credentials)
        session = baker.make_recipe('roleplay.session', players=[self.user])
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        data = {
            'name': fake.sentence(),
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_staff_not_game_master_session_partial_update_ok(self):
        self.client.credentials(**self.staff_user_credentials)
        session = baker.make_recipe('roleplay.session')
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        data = {
            'name': fake.sentence(),
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_game_master_session_update_ok(self):
        self.client.credentials(**self.user_credentials)
        session = baker.make_recipe('roleplay.session')
        session.add_game_masters(self.user)
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        data = {
            'name': fake.sentence(),
            'plot': fake.paragraph(),
            'world': self.world.pk,
            'system': random.choice(RoleplaySystems.values),
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_not_game_master_session_update_ko(self):
        self.client.credentials(**self.user_credentials)
        session = baker.make_recipe('roleplay.session', players=[self.user])
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        data = {
            'name': fake.sentence(),
            'plot': fake.paragraph(),
            'world': self.world.pk,
            'system': random.choice(RoleplaySystems.values),
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_staff_session_update_ok(self):
        self.client.credentials(**self.staff_user_credentials)
        session = baker.make_recipe('roleplay.session')
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        data = {
            'name': fake.sentence(),
            'plot': fake.paragraph(),
            'world': self.world.pk,
            'system': random.choice(RoleplaySystems.values),
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_user_game_master_session_delete_ok(self):
        self.client.credentials(**self.user_credentials)
        session = baker.make_recipe('roleplay.session')
        session.add_game_masters(self.user)
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_authenticated_user_not_game_master_session_delete_ko(self):
        self.client.credentials(**self.user_credentials)
        session = baker.make_recipe('roleplay.session', players=[self.user])
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_staff_session_delete_ok(self):
        self.client.credentials(**self.staff_user_credentials)
        session = baker.make_recipe('roleplay.session')
        url = resolve_url(f'{base_resolver}:session-detail', pk=session.pk)
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_anonymous_session_list_all_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_user_session_list_all_ko(self):
        self.client.credentials(**self.user_credentials)
        url = reverse(f'{base_resolver}:session-list-all')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_staff_session_list_all_ok(self):
        self.client.credentials(**self.staff_user_credentials)
        url = reverse(f'{base_resolver}:session-list-all')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_staff_session_list_all_correct_length_ok(self):
        self.client.credentials(**self.staff_user_credentials)
        baker.make_recipe('roleplay.session', _quantity=fake.pyint(min_value=1, max_value=10))
        url = reverse(f'{base_resolver}:session-list-all')
        response = self.client.get(url)

        self.assertEqual(Session.objects.count(), len(response.json()['results']))
