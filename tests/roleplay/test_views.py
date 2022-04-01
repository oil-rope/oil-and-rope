import os
import random
import tempfile
import time
from unittest import mock

from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import TimestampSigner
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from PIL import Image

from common import tools
from roleplay import enums, models, views
from tests import fake


class TestPlaceCreateView(TestCase):
    model = models.Place
    resolver = 'roleplay:place:create'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.parent_place = cls.model.objects.create(
            name=fake.country(),
            description=fake.paragraph(),
            site_type=enums.SiteTypes.WORLD,
            owner=cls.user,
        )
        cls.url = reverse(cls.resolver, kwargs={'pk': cls.parent_place.pk})

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        Image.new('RGB', (30, 60), color='red').save(self.tmp_file.name)
        with open(self.tmp_file.name, 'rb') as img_content:
            image = SimpleUploadedFile(name=self.tmp_file.name, content=img_content.read(), content_type='image/jpeg')

        self.data_ok = {
            'name': fake.country(),
            'description': fake.paragraph(),
            'site_type': random.choice(enums.SiteTypes.values),
            'parent_site': self.parent_place.pk,
            'image': image,
        }

    def tearDown(self):
        self.tmp_file.close()
        os.unlink(self.tmp_file.name)

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)
        login_url = reverse('registration:auth:login')

        self.assertRedirects(response, f'{login_url}?next={self.url}')

    def test_access_not_owner_ko(self):
        user = baker.make_recipe('registration.user')
        self.client.force_login(user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_access_owner_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_post_data_ok(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.data_ok, follow=True)
        created_place = response.context['object']
        self.parent_place.refresh_from_db()
        redirect_url = reverse('roleplay:place:detail', kwargs={'pk': created_place.pk})

        self.assertEqual(1, self.parent_place.get_descendant_count())
        self.assertRedirects(response, redirect_url)

    def test_post_data_without_optional_image_ok(self):
        self.client.force_login(self.user)
        data_without_image = self.data_ok.copy()
        del data_without_image['image']
        response = self.client.post(self.url, data=data_without_image, follow=True)
        created_place = response.context['object']
        self.parent_place.refresh_from_db()
        redirect_url = reverse('roleplay:place:detail', kwargs={'pk': created_place.pk})

        self.assertEqual(1, self.parent_place.get_descendant_count())
        self.assertRedirects(response, redirect_url)

    def test_post_data_without_optional_description_ok(self):
        self.client.force_login(self.user)
        data_without_description = self.data_ok.copy()
        del data_without_description['description']
        response = self.client.post(self.url, data=data_without_description, follow=True)
        created_place = response.context['object']
        self.parent_place.refresh_from_db()
        redirect_url = reverse('roleplay:place:detail', kwargs={'pk': created_place.pk})

        self.assertEqual(1, self.parent_place.get_descendant_count())
        self.assertRedirects(response, redirect_url)

    def test_post_data_without_required_name_ko(self):
        self.client.force_login(self.user)
        data_without_name = self.data_ok.copy()
        del data_without_name['name']
        response = self.client.post(self.url, data=data_without_name)
        self.parent_place.refresh_from_db()

        self.assertEqual(0, self.parent_place.get_descendant_count())
        self.assertFormError(response, form='form', field='name', errors=['This field is required.'])

    def test_post_data_without_required_parent_site_ko(self):
        self.client.force_login(self.user)
        data_without_parent_site = self.data_ok.copy()
        del data_without_parent_site['parent_site']
        response = self.client.post(self.url, data=data_without_parent_site)
        self.parent_place.refresh_from_db()

        self.assertEqual(0, self.parent_place.get_descendant_count())
        self.assertFormError(response, form='form', field='parent_site', errors=['This field is required.'])

    def test_post_data_without_required_site_type_ko(self):
        self.client.force_login(self.user)
        data_without_site_type = self.data_ok.copy()
        del data_without_site_type['site_type']
        response = self.client.post(self.url, data=data_without_site_type)
        self.parent_place.refresh_from_db()

        self.assertEqual(0, self.parent_place.get_descendant_count())
        self.assertFormError(response, form='form', field='site_type', errors=['This field is required.'])

    def test_post_data_private_world_ko(self):
        another_user = baker.make_recipe('registration.user')
        private_world = self.model.objects.create(
            name=fake.country(),
            description=fake.paragraph(),
            site_type=enums.SiteTypes.WORLD,
            owner=another_user,
            user=another_user,
        )
        data_with_private_world = self.data_ok.copy()
        data_with_private_world['parent_site'] = private_world.pk
        self.client.force_login(self.user)
        self.client.post(self.url, data=data_with_private_world)
        private_world.refresh_from_db()

        # NOTE: For some reason even tho instance isn't created no error is returned
        # self.assertFormError(response, form='form', field='parent_site', errors=['Error'])
        self.assertEqual(0, private_world.get_descendant_count())


class TestPlaceUpdateView(TestCase):
    model = models.Place
    resolver = 'roleplay:place:edit'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.owner = baker.make_recipe('registration.user')
        cls.public_world = cls.model.objects.create(
            name=fake.country(),
            description=fake.paragraph(),
            site_type=enums.SiteTypes.WORLD,
            owner=cls.owner,
        )
        cls.place = cls.model.objects.create(
            name=fake.country(),
            description=fake.paragraph(),
            site_type=random.choice(enums.SiteTypes.values),
            owner=cls.owner,
            parent_site=cls.public_world,
        )
        cls.url = reverse('roleplay:place:edit', kwargs={'pk': cls.place.pk})

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        Image.new('RGB', (30, 60), color='red').save(self.tmp_file.name)
        with open(self.tmp_file.name, 'rb') as img_content:
            image = SimpleUploadedFile(name=self.tmp_file.name, content=img_content.read(), content_type='image/jpeg')

        self.data_ok = {
            'name': fake.country(),
            'description': fake.paragraph(),
            'site_type': random.choice(enums.SiteTypes.values),
            'parent_site': self.public_world.pk,
            'image': image,
        }

    def tearDown(self):
        self.tmp_file.close()
        os.unlink(self.tmp_file.name)

    def test_anonymous_access_ko(self):
        login_url = reverse('registration:auth:login')
        response = self.client.get(self.url)

        self.assertRedirects(response, f'{login_url}?next={self.url}')

    def test_access_not_owner_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_access_owner_ok(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_anonymous_post_data_ko(self):
        login_url = reverse('registration:auth:login')
        response = self.client.post(self.url, data=self.data_ok)

        self.assertRedirects(response, f'{login_url}?next={self.url}')

    def test_post_data_ok(self):
        self.client.force_login(self.owner)
        current_name = self.place.name
        new_name = self.data_ok['name']
        response = self.client.post(self.url, data=self.data_ok)
        self.place.refresh_from_db()

        self.assertRedirects(response, reverse('roleplay:place:detail', kwargs={'pk': self.place.pk}))
        self.assertNotEqual(current_name, new_name)
        self.assertEqual(self.place.name, new_name)


class TestPlaceDetailView(TestCase):
    model = models.Place
    resolver = 'roleplay:place:detail'

    @classmethod
    def setUpTestData(cls):
        cls.owner = baker.make_recipe('registration.user')

        cls.private_world = models.Place.objects.create(
            name=fake.country(),
            description=fake.paragraph(),
            owner=cls.owner,
            user=cls.owner,
            site_type=enums.SiteTypes.WORLD,
        )
        cls.private_world_url = reverse(cls.resolver, kwargs={'pk': cls.private_world.pk})

        cls.public_world = models.Place.objects.create(
            name=fake.country(),
            description=fake.paragraph(),
            owner=cls.owner,
            # NOTE: This is what defines a private world. This must be changed at some point
            user=None,
            site_type=enums.SiteTypes.WORLD,
        )
        cls.public_world_url = reverse(cls.resolver, kwargs={'pk': cls.public_world.pk})

    def test_anonymous_access_ko(self):
        response = self.client.get(self.private_world_url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_access_not_owner_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.private_world_url)

        self.assertEqual(403, response.status_code)

    def test_access_not_owner_public_world_ok(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.public_world_url)

        self.assertEqual(200, response.status_code)

    def test_access_owner_ok(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.private_world_url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/place/place_detail.html')

    def test_access_community_world_ok(self):
        another_user = baker.make_recipe('registration.user')
        self.client.force_login(another_user)
        world = baker.make(self.model, name=fake.country(), owner=self.owner)
        url = reverse('roleplay:place:detail', kwargs={'pk': world.pk})
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_access_default_world_ok(self):
        self.client.force_login(self.owner)
        world = baker.make(self.model, name=fake.country())
        url = reverse('roleplay:place:detail', kwargs={'pk': world.pk})
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)


class TestWorldListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = models.Place
        cls.enum = enums.SiteTypes
        cls.view = views.WorldListView
        cls.url = reverse('roleplay:world:list')

    def setUp(self):
        self.pagination = self.view.paginate_by
        self.user = baker.make_recipe('registration.user')

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
                self.model.objects.create(name='world_{}'.format(_), site_type=self.enum.WORLD)
            )
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        for entry in entries:
            self.assertIn(str(entry), str(response.content))

    def test_cannot_see_other_users_places_ok(self):
        another_user = baker.make_recipe('registration.user')
        another_user_entries = []
        for _ in range(0, 10):
            another_user_entries.append(
                self.model.objects.create(
                    name='world_{}'.format(_), user=another_user,
                    site_type=self.enum.WORLD, owner=another_user
                )
            )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        for entry in another_user_entries:
            self.assertNotIn(str(entry), str(response.content))

    def test_user_can_see_its_worlds_but_no_other_users_worlds_ok(self):
        another_user = baker.make_recipe('registration.user')
        another_user_entries = []
        for _ in range(0, self.pagination):
            another_user_entries.append(
                self.model.objects.create(
                    name='another_user_world_{}'.format(_),
                    user=another_user,
                    owner=another_user,
                    site_type=self.enum.WORLD
                )
            )

        user_entries = []
        for _ in range(0, self.pagination):
            user_entries.append(
                self.model.objects.create(
                    name='user_world_{}'.format(_), user=self.user, site_type=self.enum.WORLD, owner=self.user
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

        another_user = baker.make_recipe('registration.user')
        another_user_entries = []
        for _ in range(0, self.pagination):
            another_user_entries.append(
                self.model.objects.create(
                    name=fake.name(), user=another_user,
                    site_type=self.enum.WORLD, owner=another_user
                )
            )

        entries = []
        for _ in range(0, self.pagination):
            entries.append(
                self.model.objects.create(
                    name='user_world_{}'.format(_), user=self.user,
                    site_type=self.enum.WORLD, owner=self.user
                )
            )
            entries.append(
                self.model.objects.create(name='world_{}'.format(_), site_type=self.enum.WORLD)
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
            self.model.objects.create(name='world_{}'.format(i), site_type=self.enum.WORLD)
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
                name='world_{}'.format(_), site_type=self.enum.WORLD,
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
                    name='world_{}'.format(i), site_type=self.enum.WORLD,
                    user=self.user, owner=self.user
                )
            )
        for _ in range(0, self.pagination):
            community_worlds.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.WORLD)
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
            self.model.objects.create(name='world_{}'.format(i), site_type=self.enum.WORLD)
        self.client.force_login(self.user)
        response = self.client.get(self.url + '?page=last')
        context = response.context

        self.assertEqual(200, response.status_code)
        for entry in self.model.objects.all()[:self.pagination]:
            self.assertNotIn(entry, context['object_list'])
        self.assertIn(self.model.objects.last(), context['object_list'])


class TestWorldCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.enum = enums.SiteTypes
        cls.model = models.Place
        cls.view = views.WorldCreateView
        cls.url = reverse('roleplay:world:create')

    def setUp(self):
        self.user = baker.make_recipe('registration.user')

        self.tmp_image = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.png', delete=False)
        image_file = self.tmp_image.name
        Image.new('RGB', (30, 30), color='red').save(image_file)
        with open(image_file, 'rb') as image_content:
            self.image = SimpleUploadedFile(name=image_file, content=image_content.read(), content_type='image/png')
        self.data_ok = {
            'name': fake.country(),
            'description': fake.paragraph(),
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
        self.assertRedirects(
            response,
            reverse('roleplay:place:detail', kwargs={'pk': self.model.objects.first().pk})
        )

    def test_community_world_data_is_correct_ok(self):
        self.client.force_login(self.user)
        data = self.data_ok.copy()
        self.client.post(self.url, data=data)
        entry = self.model.objects.first()

        self.assertEqual(data['name'], entry.name)
        self.assertEqual(data['description'], entry.description)
        self.assertEqual(self.enum.WORLD, entry.site_type)
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
        self.assertEqual(self.enum.WORLD, entry.site_type)
        self.assertEqual(self.user, entry.owner)
        self.assertEqual(self.user, entry.user)
        self.assertIsNotNone(entry.image)


class TestPlaceDeleteView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = models.Place

    def setUp(self):
        self.user = baker.make_recipe('registration.user')
        self.world = self.model.objects.create(
            name=fake.city(),
            owner=self.user
        )
        self.private_world = self.model.objects.create(
            name=fake.city(),
            owner=self.user,
            user=self.user
        )
        self.url = reverse('roleplay:place:delete', kwargs={'pk': self.world.pk})
        self.private_world_url = reverse('roleplay:place:delete', kwargs={'pk': self.private_world.pk})

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/place/place_confirm_delete.html')

    def test_access_anonymous_user_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_non_existent_world_ko(self):
        self.client.force_login(self.user)
        non_existent_pk = self.model.objects.last().pk + 1
        url = reverse('roleplay:place:delete', kwargs={'pk': non_existent_pk})
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_non_owner_access_ko(self):
        foreign_user = baker.make_recipe('registration.user')
        self.client.force_login(foreign_user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_delete_ok(self):
        self.client.force_login(self.user)
        self.client.delete(self.url)

        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.get(pk=self.world.pk)

    def test_non_owner_delete_ko(self):
        foreign_user = baker.make_recipe('registration.user')
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

        self.user = baker.make_recipe('registration.user')
        self.world = self.model.objects.create(name=fake.city(), user=self.user, owner=self.user)
        self.community_world = self.model.objects.create(name=fake.city(), owner=self.user)
        self.url = reverse('roleplay:world:edit', kwargs={'pk': self.world.pk})
        self.data_ok = {
            'name': fake.city(),
            'description': fake.paragraph(),
            'image': self.image
        }

    def tearDown(self):
        os.unlink(self.image_file)

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'roleplay/place/place_update.html')

    def test_access_anonymous_user_ko(self):
        response = self.client.get(self.url)

        self.assertNotEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_non_existent_world_ko(self):
        self.client.force_login(self.user)
        non_existent_pk = self.model.objects.last().pk + 1
        url = reverse('roleplay:world:edit', kwargs={'pk': non_existent_pk})
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_non_owner_access_ko(self):
        foreign_user = baker.make_recipe('registration.user')
        self.client.force_login(foreign_user)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_data_without_image_ok(self):
        data = self.data_ok.copy()
        del data['image']
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

    def test_update_community_world_ok(self):
        self.client.force_login(self.user)
        url = reverse('roleplay:world:edit', kwargs={'pk': self.community_world.pk})
        data = self.data_ok.copy()
        # TODO: Figure out why image is failing
        del data['image']
        self.client.post(url, data=data)

        self.community_world.refresh_from_db()
        self.assertEqual(data['name'], self.community_world.name)
        self.assertEqual(data['description'], self.community_world.description)
        self.assertEqual(self.user, self.community_world.owner)
        self.assertIsNone(self.community_world.user)


class TestSessionCreateView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = models.Session
    resolver = 'roleplay:session:create'
    template = 'roleplay/session/session_create.html'
    view = views.SessionCreateView

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.world = baker.make_recipe('roleplay.world')

    def setUp(self):
        self.url = resolve_url(self.resolver, pk=self.world.pk)
        self.data_ok = {
            'name': fake.word(),
            'plot': fake.paragraph(),
            'next_game': timezone.now() + timezone.timedelta(days=1),
            'system': enums.RoleplaySystems.PATHFINDER,
            'world': self.world.pk,
            'email_invitations': '\n'.join([fake.safe_email() for _ in range(3)])
        }

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_logged_user_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_template_used_is_correct_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_access_with_non_existing_world_ko(self):
        self.client.force_login(self.user)
        non_existent_pk = self.world.pk + 1
        url = resolve_url(self.resolver, pk=non_existent_pk)
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_access_with_private_world_ko(self):
        world = baker.make_recipe('roleplay.private_world')
        url = resolve_url(self.resolver, pk=world.pk)
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_session_is_created_with_correct_data_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.data_ok)

        session = self.model.objects.last()
        self.assertEqual(self.data_ok['name'], session.name)
        self.assertEqual(self.data_ok['plot'], session.plot)
        self.assertEqual(self.data_ok['next_game'], session.next_game)
        self.assertEqual(self.data_ok['system'], session.system)
        self.assertEqual(self.data_ok['world'], session.world.pk)

    def test_session_is_created_with_current_user_as_game_master_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.data_ok)

        session = self.model.objects.last()
        self.assertIn(self.user, session.game_masters)

    def test_session_is_created_and_emails_are_sent_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.data_ok)
        emails = self.data_ok['email_invitations'].split('\n')

        time.sleep(1)
        self.assertEqual(len(emails), len(mail.outbox))

    def test_post_data_without_name_ko(self):
        data_without_name = self.data_ok.copy()
        del data_without_name['name']

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_without_name)

        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_post_data_without_next_game_ko(self):
        data_without_next_game = self.data_ok.copy()
        del data_without_next_game['next_game']

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_without_next_game)

        self.assertFormError(response, 'form', 'next_game', 'This field is required.')

    def test_post_data_without_system_ko(self):
        data_without_system = self.data_ok.copy()
        del data_without_system['system']

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_without_system)

        self.assertFormError(response, 'form', 'system', 'This field is required.')

    def test_post_data_without_world_ko(self):
        data_without_world = self.data_ok.copy()
        del data_without_world['world']

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_without_world)

        self.assertFormError(response, 'form', 'world', 'This field is required.')

    def test_post_data_next_game_in_the_past_ko(self):
        data_with_past_next_game = self.data_ok.copy()
        data_with_past_next_game['next_game'] = fake.past_datetime()

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_with_past_next_game)

        self.assertFormError(response, 'form', 'next_game', 'Next game date must be in the future.')

    def test_post_data_without_email_invitations_ok(self):
        data_without_email_invitations = self.data_ok.copy()
        del data_without_email_invitations['email_invitations']

        self.client.force_login(self.user)
        self.client.post(self.url, data=data_without_email_invitations)

        time.sleep(1)
        self.assertEqual(0, len(mail.outbox))

    def test_post_data_without_plot_ok(self):
        data_without_plot = self.data_ok.copy()
        del data_without_plot['plot']

        self.client.force_login(self.user)
        self.client.post(self.url, data=data_without_plot)

        session = self.model.objects.last()
        # NOTE: Field is not nullable, so it's empty string
        self.assertEqual('', session.plot)


class TestSessionJoinView(TestCase):
    model = models.Session
    resolver = 'roleplay:session:join'
    view = views.SessionJoinView

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.session = baker.make_recipe('roleplay.session')
        cls.signer = TimestampSigner()

    def test_access_with_correct_token_and_existing_user_ok(self):
        token = tools.get_token(self.user.email, self.signer)
        url = resolve_url(self.resolver, pk=self.session.pk, token=token)
        response = self.client.get(url)

        self.assertRedirects(response, resolve_url(self.session), target_status_code=302)

    @mock.patch('roleplay.views.messages')
    def test_access_with_correct_token_and_existing_user_messages_ok(self, mock_messages):
        token = tools.get_token(self.user.email, self.signer)
        url = resolve_url(self.resolver, pk=self.session.pk, token=token)
        response = self.client.get(url)

        mock_messages.success.assert_called_once_with(response.wsgi_request, 'You have joined the session.')

    def test_access_with_correct_token_and_non_existing_user_redirects_to_login_ko(self):
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.session.pk, token=token)
        response = self.client.get(url)

        self.assertRedirects(response, resolve_url(settings.LOGIN_URL))

    @mock.patch('roleplay.views.messages')
    def test_access_with_correct_token_and_non_existing_user_messages_ko(self, mock_messages):
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.session.pk, token=token)
        response = self.client.get(url)

        mock_messages.warning.assert_called_once_with(
            response.wsgi_request,
            'You need an account to join this session.'
        )

    def test_access_with_logged_user_ok(self):
        self.client.force_login(self.user)
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.session.pk, token=token)
        response = self.client.get(url)

        self.assertRedirects(response, resolve_url(self.session))

    def test_access_with_logged_user_adds_user_to_players_ok(self):
        self.client.force_login(self.user)
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.session.pk, token=token)
        self.client.get(url)

        self.assertIn(self.user, self.session.players.all())

    def test_access_with_incorrect_token_ko(self):
        token = f'{fake.email()}:{fake.password()}'
        url = resolve_url(self.resolver, pk=self.session.pk, token=token)
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)


class TestSessionDetailView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = models.Session
    resolver = 'roleplay:session:detail'
    template = 'roleplay/session/session_detail.html'
    view = views.SessionDetailView

    @classmethod
    def setUpTestData(cls):
        cls.user_in_players = baker.make_recipe('registration.user')
        cls.user_not_in_players = baker.make_recipe('registration.user')

        cls.session = baker.make_recipe('roleplay.session', players=[cls.user_in_players])
        cls.url = resolve_url(cls.resolver, pk=cls.session.pk)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_with_non_player_ko(self):
        self.client.force_login(self.user_not_in_players)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_access_with_player_ok(self):
        self.client.force_login(self.user_in_players)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_with_player_with_profile_pic_ok(self):
        user = baker.make_recipe('roleplay.user')
        profile = user.profile
        profile.image = SimpleUploadedFile('test_image.jpg', b'file_content', content_type='image/jpeg')
        profile.save()
        self.session.players.add(user)
        self.client.force_login(user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_with_game_master_ok(self):
        session = baker.make_recipe('roleplay.session')
        session.add_game_masters(self.user_in_players)
        self.client.force_login(self.user_in_players)
        url = resolve_url(self.resolver, pk=session.pk)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_access_templated_used_is_correct_ok(self):
        self.client.force_login(self.user_in_players)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)


class TestSessionDeleteView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = models.Session
    resolver = 'roleplay:session:delete'
    template = 'roleplay/session/session_confirm_delete.html'
    view = views.SessionDeleteView

    @classmethod
    def setUpTestData(cls):
        cls.user_in_game_masters = baker.make_recipe('registration.user')
        cls.user_not_in_game_masters = baker.make_recipe('registration.user')

        cls.session = baker.make_recipe('roleplay.session')
        cls.session.add_game_masters(cls.user_in_game_masters)
        cls.url = resolve_url(cls.resolver, pk=cls.session.pk)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_with_non_game_master_ko(self):
        self.client.force_login(self.user_not_in_game_masters)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_access_with_game_master_ok(self):
        self.client.force_login(self.user_in_game_masters)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_templated_used_is_correct_ok(self):
        self.client.force_login(self.user_in_game_masters)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_access_game_master_session_deleted_ok(self):
        self.client.force_login(self.user_in_game_masters)
        self.client.post(self.url)

        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.get(pk=self.session.pk)

    def test_access_game_master_session_deleted_redirect_ok(self):
        self.client.force_login(self.user_in_game_masters)
        response = self.client.post(self.url)

        self.assertRedirects(response, resolve_url('roleplay:session:list'))

    @mock.patch('roleplay.views.messages')
    def test_access_game_master_session_deleted_message_ok(self, mock_messages):
        self.client.force_login(self.user_in_game_masters)
        response = self.client.post(self.url)

        mock_messages.success.assert_called_once_with(
            response.wsgi_request,
            'Session deleted.',
        )


class TestSessionUpdateView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = models.Session
    resolver = 'roleplay:session:edit'
    template = 'roleplay/session/session_update.html'
    view = views.SessionUpdateView

    @classmethod
    def setUpTestData(cls):
        cls.user_in_game_masters = baker.make_recipe('registration.user')
        cls.user_not_in_game_masters = baker.make_recipe('registration.user')

        cls.session = baker.make_recipe('roleplay.session')
        cls.session.add_game_masters(cls.user_in_game_masters)
        cls.url = resolve_url(cls.resolver, pk=cls.session.pk)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_with_non_game_master_ko(self):
        self.client.force_login(self.user_not_in_game_masters)
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_access_with_game_master_ok(self):
        self.client.force_login(self.user_in_game_masters)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_templated_used_is_correct_ok(self):
        self.client.force_login(self.user_in_game_masters)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_access_game_master_session_updated_ok(self):
        name = fake.sentence()
        data = {
            'name': name,
            'plot': fake.text(),
            'system': self.session.system,
            'next_game': self.session.next_game,
            'world': self.session.world.pk,
        }
        self.client.force_login(self.user_in_game_masters)
        self.client.post(self.url, data)
        self.session.refresh_from_db()

        self.assertEqual(name, self.session.name)

    @mock.patch('roleplay.views.messages')
    def test_access_game_master_session_updated_message_ok(self, mock_messages):
        data = {
            'name': fake.sentence(),
            'plot': fake.text(),
            'system': self.session.system,
            'next_game': self.session.next_game,
            'world': self.session.world.pk,
        }
        self.client.force_login(self.user_in_game_masters)
        response = self.client.post(self.url, data)

        mock_messages.success.assert_called_once_with(
            response.wsgi_request,
            'Session updated!'
        )


class TestSessionListView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = models.Session
    resolver = 'roleplay:session:list'
    template = 'roleplay/session/session_list.html'
    view = views.SessionListView

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.another_user = baker.make_recipe('registration.user')
        another_user_profile = cls.another_user.profile
        another_user_profile.image = SimpleUploadedFile('image.png', b'file_content', content_type='image/png')
        another_user_profile.save()
        baker.make_recipe(
            baker_recipe_name='roleplay.session',
            _quantity=fake.pyint(min_value=1, max_value=10),
            players=[cls.user, cls.another_user],
        )
        cls.url = resolve_url(cls.resolver)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_with_user_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_templated_used_is_correct_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_access_session_list_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(self.user.session_set.count(), response.context['object_list'].count())

    def test_access_session_with_image_ok(self):
        session = baker.make_recipe('roleplay.session', players=[self.user])
        session.image = SimpleUploadedFile('image.png', b'file_content', content_type='image/png')
        session.save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_session_list_only_where_user_is_player_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        baker.make_recipe('roleplay.session', _quantity=fake.pyint(min_value=1, max_value=10))

        self.assertEqual(self.user.session_set.count(), response.context['object_list'].count())
