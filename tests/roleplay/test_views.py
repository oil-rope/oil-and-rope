import os
import tempfile

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from roleplay import models, views


class TestWorldListView(TestCase):
    view = views.WorldListView

    def setUp(self):
        self.faker = Faker()
        self.model = models.Place
        self.pagination = views.WorldListView.paginate_by
        self.user = baker.make(get_user_model())
        self.url = reverse('roleplay:world_list')

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
        for _ in range(0, self.pagination):
            entries.append(
                self.model.objects.create(name='world_{}'.format(_), site_type=self.model.WORLD)
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
                self.model.objects.create(name='world_{}'.format(_), user=another_user, site_type=self.model.WORLD)
            )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        for entry in another_user_entries:
            self.assertNotIn(str(entry), str(response.content))

    def test_user_can_see_its_worlds_but_no_other_users_worlds_ok(self):
        another_user = baker.make(get_user_model())
        another_user_entries = []
        for _ in range(0, self.pagination):
            another_user_entries.append(
                self.model.objects.create(name='another_user_'.format(_), user=another_user, site_type=self.model.WORLD)
            )

        user_entries = []
        for _ in range(0, self.pagination):
            user_entries.append(
                self.model.objects.create(name='user_world_{}'.format(_), user=self.user, site_type=self.model.WORLD)
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
        for _ in range(0, self.pagination):
            another_user_entries.append(
                self.model.objects.create(name=self.faker.name(), user=another_user, site_type=self.model.WORLD)
            )

        entries = []
        for _ in range(0, self.pagination):
            entries.append(
                self.model.objects.create(name='user_world_{}'.format(_), user=self.user, site_type=self.model.WORLD)
            )
            entries.append(
                self.model.objects.create(name='world_{}'.format(_), site_type=self.model.WORLD)
            )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        for entry in another_user_entries:
            self.assertNotIn(str(entry), str(response.content))

        for entry in entries:
            self.assertIn(str(entry), str(response.content))

    def test_non_existent_community_worlds_pagination_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?page=2')

        self.assertEqual(404, response.status_code)

    def test_correct_community_worlds_are_paginated_ok(self):
        for _ in range(0, self.pagination + 1):
            self.model.objects.create(name='world_{}'.format(_), site_type=self.model.WORLD)
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?page=1')

        visible_entries = self.model.objects.all()[:self.pagination]
        last_entry = self.model.objects.last()

        for entry in visible_entries:
            self.assertIn(str(entry), str(response.content))
        self.assertNotIn(str(last_entry), str(response.content))

        response = self.client.get(self.url + '?page=2')

        for entry in visible_entries:
            self.assertNotIn(str(entry), str(response.content))
        self.assertIn(str(last_entry), str(response.content))

    def test_non_existent_user_worlds_pagination_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?{}=2'.format(self.view.user_worlds_page_kwarg))

        self.assertEqual(404, response.status_code)

    def test_correct_user_worlds_are_paginated_ok(self):
        for _ in range(0, self.pagination + 1):
            self.model.objects.create(name='world_{}'.format(_), site_type=self.model.WORLD, user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?{}=1'.format(self.view.user_worlds_page_kwarg))

        visible_entries = self.model.objects.all()[:self.pagination]
        last_entry = self.model.objects.last()

        for entry in visible_entries:
            self.assertIn(str(entry), str(response.content))
        self.assertNotIn(str(last_entry), str(response.content))

        response = self.client.get(self.url + '?{}=2'.format(self.view.user_worlds_page_kwarg))

        for entry in visible_entries:
            self.assertNotIn(str(entry), str(response.content))
        self.assertIn(str(last_entry), str(response.content))

    def test_user_worlds_are_paginated_community_worlds_are_not_ko(self):
        community_worlds = []
        user_worlds = []
        for _ in range(0, self.pagination + 1):
            user_worlds.append(
                self.model.objects.create(name='world_{}'.format(_), site_type=self.model.WORLD, user=self.user)
            )
        for _ in range(0, self.pagination):
            community_worlds.append(
                self.model.objects.create(name=self.faker.name(), site_type=self.model.WORLD)
            )
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?{}=1&page=1'.format(self.view.user_worlds_page_kwarg))

        for entry in community_worlds[:self.pagination - 1]:
            self.assertIn(str(entry), str(response.content))
        for entry in user_worlds[:self.pagination]:
            self.assertIn(str(entry), str(response.content))
        self.assertNotIn(str(user_worlds[self.pagination]), str(response.content))

        response = self.client.get(self.url + '?{}=2&page=2'.format(self.view.user_worlds_page_kwarg))

        self.assertEqual(404, response.status_code)

        response = self.client.get(self.url + '?{}=2&page=1'.format(self.view.user_worlds_page_kwarg))
        for entry in community_worlds[:self.pagination - 1]:
            self.assertIn(str(entry), str(response.content))
        for entry in user_worlds[:self.pagination]:
            self.assertNotIn(str(entry), str(response.content))
        self.assertIn(str(user_worlds[self.pagination]), str(response.content))

    def test_non_numeric_page_kwarg_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?page=random')

        self.assertEqual(404, response.status_code)

    def test_last_page_ok(self):
        for _ in range(0, self.pagination + 1):
            self.model.objects.create(name='world_{}'.format(_), site_type=self.model.WORLD)
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?page=last')

        self.assertEqual(200, response.status_code)
        for entry in self.model.objects.all()[:self.pagination]:
            self.assertNotIn(str(entry), str(response.content))
        self.assertIn(str(self.model.objects.last()), str(response.content))


class TestWorldCreateView(TestCase):
    model = models.Place
    view = views.WorldCreateView

    def setUp(self):
        self.faker = Faker()
        self.url = reverse('roleplay:world_create')
        self.user = baker.make(get_user_model())

        self.tmp_image = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.png', delete=False)
        image_file = self.tmp_image.name
        Image.new('RGB', (30, 30), color='red').save(image_file)
        image_content = open(image_file, 'rb').read()
        self.image = SimpleUploadedFile(name=image_file, content=image_content, content_type='image/png')
        self.data_ok = {
            'name': self.faker.country(),
            'description': self.faker.paragraph(),
            'image': self.image
        }

    def tearDown(self):
        # Delete tmp file
        self.tmp_image.close()
        os.unlink(self.tmp_image.name)

        # Delete media files created by tests
        for image in self.model.objects.values_list('image', flat=True):
            os.unlink('{}/{}'.format(settings.MEDIA_ROOT, image))

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/world_create.html')

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_create_community_world_ok(self):
        self.client.force_login(self.user)
        data = self.data_ok.copy()
        response = self.client.post(self.url, data=data)

        self.assertTrue(self.model.objects.exists())
        self.assertEqual(1, self.model.objects.count())
        self.assertRedirects(response, reverse('roleplay:world_detail', kwargs={'pk': self.model.objects.first().pk}))

    def test_community_world_data_is_correct_ok(self):
        self.client.force_login(self.user)
        data = self.data_ok.copy()
        self.client.post(self.url, data=data)
        entry = self.model.objects.first()

        self.assertEqual(data['name'], entry.name)
        self.assertEqual(data['description'], entry.description)
        self.assertEqual(self.model.WORLD, entry.site_type)
        self.assertIsNone(entry.user)
        self.assertIsNotNone(entry.image)

    def test_community_world_missing_name_ko(self):
        data = self.data_ok.copy()
        del data['name']
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data)

        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_user_world_data_is_correct_ok(self):
        self.client.force_login(self.user)
        data = self.data_ok.copy()
        self.client.post(self.url + '?user', data=data)
        entry = self.model.objects.first()

        self.assertEqual(data['name'], entry.name)
        self.assertEqual(data['description'], entry.description)
        self.assertEqual(self.model.WORLD, entry.site_type)
        self.assertEqual(self.user, entry.user)
        self.assertIsNotNone(entry.image)


class TestWorldDetailView(TestCase):
    model = models.Place
    view = views.WorldDetailView

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model())
        self.world = baker.make(models.Place, name=self.faker.country())
        self.url = reverse('roleplay:world_detail', kwargs={'pk': self.world.pk})

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/world_detail.html')

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)
