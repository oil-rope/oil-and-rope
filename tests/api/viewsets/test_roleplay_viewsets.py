from django.apps import apps
from django.shortcuts import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models
from roleplay.enums import SiteTypes, RoleplaySystems

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
PlayerInSession = apps.get_model(models.ROLEPLAY_PLAYER_IN_SESSION)
Race = apps.get_model(models.RACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)
User = apps.get_model(models.USER_MODEL)

fake = Faker()

base_resolver = 'api:roleplay'


class TestRoleplayAPIRoot(APITestCase):

    def test_anonymous_list_urls_ok(self):
        url = reverse(f'{base_resolver}:api-root')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)


# noinspection DuplicatedCode
class TestDomainViewSet(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.list_url = reverse(f'{base_resolver}:domain-list')
        cls.model = Domain

        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)

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
        domain = baker.make(self.model)
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_admin_domain_detail_ok(self):
        self.client.force_login(self.admin_user)
        domain = baker.make(self.model)
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
        domain = baker.make(self.model)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_partial_update_ok(self):
        self.client.force_login(self.admin_user)
        domain = baker.make(self.model)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.patch(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_update_ko(self):
        self.client.force_login(self.user)
        domain = baker.make(self.model)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_update_ok(self):
        self.client.force_login(self.admin_user)
        domain = baker.make(self.model)
        data = {
            'name': fake.word(),
            'description': fake.paragraph(),
        }
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.put(url, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_delete_ko(self):
        self.client.force_login(self.user)
        domain = baker.make(self.model)
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_admin_delete_ok(self):
        self.client.force_login(self.admin_user)
        domain = baker.make(self.model)
        url = reverse(f'{base_resolver}:domain-detail', kwargs={'pk': domain.pk})
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


# noinspection DuplicatedCode
class TestPlaceViewSet(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.model = Place
        cls.list_url = reverse(f'{base_resolver}:place-list')

        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)

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


# noinspection DuplicatedCode
class TestRaceViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Race
        cls.list_url = reverse(f'{base_resolver}:race-list')

        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)

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


# noinspection DuplicatedCode
class TestSessionViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Session
        cls.list_url = reverse(f'{base_resolver}:session-list')

        cls.user = baker.make(User)
        cls.admin_user = baker.make(User, is_staff=True)
        cls.world = baker.make(Place, site_type=SiteTypes.WORLD)

    def test_anonymous_session_list_ko(self):
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_authenticated_not_admin_session_list_ok(self):
        # User sessions
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), players=[self.user], world=self.world
        )
        # Other's sessions
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), players=[self.admin_user],
            world=self.world
        )
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.user.session_set.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_session_list_ok(self):
        # User sessions
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), players=[self.user], world=self.world
        )
        # Other's sessions
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), players=[self.admin_user],
            world=self.world
        )
        self.client.force_login(self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.model.objects.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_not_admin_user_in_players_retrieve_session_ok(self):
        session = baker.make(self.model, players=[self.user], world=self.world)
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_authenticated_not_admin_user_not_in_players_retrieve_session_ok(self):
        session = baker.make(self.model, world=self.world)
        url = reverse(f'{base_resolver}:session-detail', kwargs={'pk': session.pk})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_authenticated_not_admin_gm_sessions_list_ok(self):
        # User sessions
        sessions = baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), players=[self.user], world=self.world
        )
        for session in sessions:
            PlayerInSession.objects.create(
                player=self.user,
                session=session,
                is_game_master=True
            )
        # Other's sessions
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), players=[self.admin_user],
            world=self.world
        )
        url = reverse(f'{base_resolver}:session-user-list')
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.user.gm_sessions.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_admin_gm_sessions_list_ok(self):
        # User sessions
        sessions = baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), players=[self.user], world=self.world
        )
        for session in sessions:
            PlayerInSession.objects.create(
                player=self.admin_user,
                session=session,
                is_game_master=True
            )
        # Other's sessions
        baker.make(
            _model=self.model, _quantity=fake.pyint(min_value=1, max_value=10), players=[self.user],
            world=self.world
        )
        url = reverse(f'{base_resolver}:session-user-list')
        self.client.force_login(self.admin_user)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = self.admin_user.gm_sessions.count()
        data = response.json()['results']

        self.assertEqual(expected_data, len(data))

    def test_authenticated_not_admin_create_session_ok(self):
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

    def test_authenticated_admin_create_session_ok(self):
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
