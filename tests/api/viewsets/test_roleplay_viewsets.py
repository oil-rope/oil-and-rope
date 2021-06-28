from django.apps import apps
from django.shortcuts import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import models

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
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
