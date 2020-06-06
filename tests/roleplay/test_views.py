import os
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker
from model_bakery import baker
from PIL import Image

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
        self.assertTemplateUsed(response, 'roleplay/world/world_list.html')

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
                self.model.objects.create(
                    name='world_{}'.format(_), user=another_user,
                    site_type=self.model.WORLD, owner=another_user
                )
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
                self.model.objects.create(
                    name='another_user_world_{}'.format(_),
                    user=another_user,
                    owner=another_user,
                    site_type=self.model.WORLD
                )
            )

        user_entries = []
        for _ in range(0, self.pagination):
            user_entries.append(
                self.model.objects.create(
                    name='user_world_{}'.format(_), user=self.user, site_type=self.model.WORLD, owner=self.user
                )
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
                self.model.objects.create(
                    name=self.faker.name(), user=another_user,
                    site_type=self.model.WORLD, owner=another_user
                )
            )

        entries = []
        for _ in range(0, self.pagination):
            entries.append(
                self.model.objects.create(
                    name='user_world_{}'.format(_), user=self.user,
                    site_type=self.model.WORLD, owner=self.user
                )
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
        for i in range(0, self.pagination + 1):
            self.model.objects.create(name='world_{}'.format(i), site_type=self.model.WORLD)
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?page=1')
        context = response.context

        community_worlds_visible = self.model.objects.all()[:self.pagination]
        last_entry = self.model.objects.last()

        for world in community_worlds_visible:
            self.assertIn(world, context['object_list'])
        self.assertNotIn(last_entry, context['object_list'])

        response = self.client.get(self.url + '?page=2')
        context = response.context

        for world in community_worlds_visible:
            self.assertNotIn(world, context['object_list'])
        self.assertIn(last_entry, context['object_list'])

    def test_non_existent_user_worlds_pagination_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?{}=2'.format(self.view.user_worlds_page_kwarg))

        self.assertEqual(404, response.status_code)

    def test_correct_user_worlds_are_paginated_ok(self):
        for _ in range(0, self.pagination + 1):
            self.model.objects.create(
                name='world_{}'.format(_), site_type=self.model.WORLD,
                user=self.user, owner=self.user
            )
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?{}=1'.format(self.view.user_worlds_page_kwarg))
        context = response.context

        user_worlds_visible = self.model.objects.all()[:self.pagination]
        last_entry = self.model.objects.last()

        for world in user_worlds_visible:
            self.assertIn(world, context['user_worlds'])
        self.assertNotIn(last_entry, context['user_worlds'])

        response = self.client.get(self.url + '?{}=2'.format(self.view.user_worlds_page_kwarg))
        context = response.context

        for entry in user_worlds_visible:
            self.assertNotIn(entry, context['user_worlds'])
        self.assertIn(last_entry, context['user_worlds'])

    def test_user_worlds_are_paginated_community_worlds_are_not_ko(self):
        community_worlds = []
        user_worlds = []
        for i in range(0, self.pagination + 1):
            user_worlds.append(
                self.model.objects.create(
                    name='world_{}'.format(i), site_type=self.model.WORLD,
                    user=self.user, owner=self.user
                )
            )
        for _ in range(0, self.pagination):
            community_worlds.append(
                self.model.objects.create(name=self.faker.name(), site_type=self.model.WORLD)
            )
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?{}=1&page=1'.format(self.view.user_worlds_page_kwarg))
        context = response.context

        for entry in community_worlds[:self.pagination - 1]:
            self.assertIn(entry, context['object_list'])
        for entry in user_worlds[:self.pagination]:
            self.assertIn(entry, context['user_worlds'])
        self.assertNotIn(user_worlds[self.pagination], context['user_worlds'])

        response = self.client.get(self.url + '?{}=2&page=2'.format(self.view.user_worlds_page_kwarg))

        self.assertEqual(404, response.status_code)

        response = self.client.get(self.url + '?{}=2&page=1'.format(self.view.user_worlds_page_kwarg))
        context = response.context
        for entry in community_worlds[:self.pagination - 1]:
            self.assertIn(entry, context['object_list'])
        for entry in user_worlds[:self.pagination]:
            self.assertNotIn(entry, context['user_worlds'])
        self.assertIn(user_worlds[self.pagination], context['user_worlds'])

    def test_non_numeric_page_kwarg_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?page=random')

        self.assertEqual(404, response.status_code)

    def test_last_page_ok(self):
        for i in range(0, self.pagination + 1):
            self.model.objects.create(name='world_{}'.format(i), site_type=self.model.WORLD)
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?page=last')
        context = response.context

        self.assertEqual(200, response.status_code)
        for entry in self.model.objects.all()[:self.pagination]:
            self.assertNotIn(entry, context['object_list'])
        self.assertIn(self.model.objects.last(), context['object_list'])


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
        with open(image_file, 'rb') as image_content:
            self.image = SimpleUploadedFile(name=image_file, content=image_content.read(), content_type='image/png')
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
        self.assertTemplateUsed(response, 'roleplay/world/world_create.html')

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
        self.assertEqual(self.user, entry.owner)
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
        self.assertEqual(self.user, entry.owner)
        self.assertEqual(self.user, entry.user)
        self.assertIsNotNone(entry.image)


class TestWorldDetailView(TestCase):
    model = models.Place
    view = views.WorldDetailView

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model())
        self.world = baker.make(models.Place, name=self.faker.country(), owner=self.user, user=self.user)
        self.url = reverse('roleplay:world_detail', kwargs={'pk': self.world.pk})

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/world/world_detail.html')

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_access_community_world_ok(self):
        another_user = baker.make(get_user_model())
        self.client.force_login(another_user)
        world = baker.make(self.model, name=self.faker.country(), owner=self.user)
        url = reverse('roleplay:world_detail', kwargs={'pk': world.pk})
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_access_default_world_ok(self):
        self.client.force_login(self.user)
        world = baker.make(self.model, name=self.faker.country())
        url = reverse('roleplay:world_detail', kwargs={'pk': world.pk})
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_access_not_owner_ko(self):
        another_user = baker.make(get_user_model())
        self.client.force_login(another_user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)


class TestWorldDeleteView(TestCase):
    model = models.Place

    def setUp(self):
        self.faker = Faker()
        self.user = baker.make(get_user_model())
        self.world = self.model.objects.create(
            name=self.faker.city(),
            owner=self.user
        )
        self.private_world = self.model.objects.create(
            name=self.faker.city(),
            owner=self.user,
            user=self.user
        )
        self.url = reverse('roleplay:world_delete', kwargs={'pk': self.world.pk})
        self.private_world_url = reverse('roleplay:world_delete', kwargs={'pk': self.private_world.pk})

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/world/world_confirm_delete.html')

    def test_access_anonymous_user_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_non_existent_world_ko(self):
        self.client.force_login(self.user)
        non_existent_pk = self.model.objects.last().pk + 1
        url = reverse('roleplay:world_delete', kwargs={'pk': non_existent_pk})
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_non_owner_access_ko(self):
        foreign_user = baker.make(get_user_model())
        self.client.force_login(foreign_user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    # noinspection PyTypeChecker
    def test_delete_ok(self):
        self.client.force_login(self.user)
        self.client.delete(self.url)

        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.get(pk=self.world.pk)

    def test_non_owner_delete_ko(self):
        foreign_user = baker.make(get_user_model())
        self.client.force_login(foreign_user)
        response = self.client.delete(self.url)

        self.assertEqual(403, response.status_code)


class TestWorldUpdateView(TestCase):
    model = models.Place
    view = views.WorldUpdateView

    def setUp(self):
        tmp_image = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.png', delete=False)
        self.image_file = tmp_image.name
        Image.new('RGB', (30, 30), color='red').save(self.image_file)
        with open(self.image_file, 'rb') as image:
            self.image = SimpleUploadedFile(name=self.image_file, content=image.read(), content_type='image/png')

        self.faker = Faker()
        self.user = baker.make(get_user_model())
        self.world = self.model.objects.create(name=self.faker.city(), user=self.user, owner=self.user)
        self.url = reverse('roleplay:world_edit', kwargs={'pk': self.world.pk})
        self.data_ok = {
            'name': self.faker.city(),
            'description': self.faker.paragraph(),
            'image': self.image
        }

    def tearDown(self):
        os.unlink(self.image_file)

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/world/world_update.html')

    def test_access_anonymous_user_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_non_existent_world_ko(self):
        self.client.force_login(self.user)
        non_existent_pk = self.model.objects.last().pk + 1
        url = reverse('roleplay:world_edit', kwargs={'pk': non_existent_pk})
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_non_owner_access_ko(self):
        foreign_user = baker.make(get_user_model())
        self.client.force_login(foreign_user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_data_without_image_ok(self):
        data = {
            'name': self.faker.city(),
            'description': self.faker.paragraph()
        }
        self.client.force_login(self.user)
        self.client.post(self.url, data=data)

        self.world.refresh_from_db()
        self.assertEqual(data['name'], self.world.name)
        self.assertEqual(data['description'], self.world.description)

    def test_data_with_image_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.data_ok)

        self.world.refresh_from_db()
        self.assertEqual(self.data_ok['name'], self.world.name)
        self.assertEqual(self.data_ok['description'], self.world.description)

        # Okay now let's check if image is correct
        with open(self.world.image.path, 'rb') as image:
            world_image = image.read()
        with open(self.image_file, 'rb') as image:
            data_image = image.read()
        self.assertEqual(data_image, world_image)

    def test_data_without_name_ko(self):
        self.client.force_login(self.user)
        data_ko = self.data_ok.copy()
        del data_ko['name']
        response = self.client.post(self.url, data=data_ko)

        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_data_without_description_ok(self):
        self.client.force_login(self.user)
        data_without_description = self.data_ok.copy()
        del data_without_description['description']
        self.client.post(self.url, data=data_without_description)

        self.world.refresh_from_db()
        self.assertEqual(data_without_description['name'], self.world.name)
        self.assertEqual('', self.world.description)

        with open(self.world.image.path, 'rb') as image:
            world_image = image.read()
        with open(self.image_file, 'rb') as image:
            data_image = image.read()
        self.assertEqual(data_image, world_image)
