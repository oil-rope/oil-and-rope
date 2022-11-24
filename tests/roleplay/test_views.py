import os
import random
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import TimestampSigner
from django.shortcuts import resolve_url
from django.test import RequestFactory, TestCase
from django.urls import reverse
from model_bakery import baker
from PIL import Image

from chat.models import Chat
from common import tools
from common.models import Vote
from registration.models import User
from roleplay import enums, views
from roleplay.models import Campaign, Place, Race, Session
from tests.mocks import discord
from tests.utils import fake

from ..utils import generate_place


class TestPlaceCreateView(TestCase):
    model = Place
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


class TestPlaceUpdateView(TestCase):
    model = Place
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
    model = Place
    resolver = 'roleplay:place:detail'

    @classmethod
    def setUpTestData(cls):
        cls.owner = baker.make_recipe('registration.user')

        cls.private_world = generate_place(
            name=fake.country(),
            description=fake.paragraph(),
            owner=cls.owner,
            is_public=False,
            site_type=enums.SiteTypes.WORLD,
        )
        cls.private_world_url = reverse(cls.resolver, kwargs={'pk': cls.private_world.pk})

        cls.public_world = generate_place(
            name=fake.country(),
            description=fake.paragraph(),
            owner=cls.owner,
            is_public=True,
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
        world = generate_place(name=fake.country(), is_public=True)
        url = reverse('roleplay:place:detail', kwargs={'pk': world.pk})
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)


class TestPlaceDeleteView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Place

    def setUp(self):
        self.user = baker.make_recipe('registration.user')
        self.world = generate_place(
            name=fake.city(),
            owner=self.user
        )
        self.private_world = generate_place(
            name=fake.city(),
            owner=self.user,
            is_public=False,
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


class TestWorldListView(TestCase):
    model = Place
    resolver = 'roleplay:world:list'
    view = views.WorldListView

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')
        cls.public_worlds_count = fake.pyint(min_value=2, max_value=cls.view.paginate_by)
        cls.private_worlds_count = fake.pyint(min_value=2, max_value=cls.view.paginate_by)
        cls.url = resolve_url(cls.resolver)

    def setUp(self) -> None:
        self.public_worlds = generate_place(self.public_worlds_count, is_public=True, site_type=enums.SiteTypes.WORLD)
        self.private_worlds = generate_place(
            self.private_worlds_count, is_public=False, owner=self.user, site_type=enums.SiteTypes.WORLD,
        )

    def test_anonymous_access_ko(self):
        login_url = resolve_url(settings.LOGIN_URL)
        expected_url = f'{login_url}?next={self.url}'
        response = self.client.get(self.url)

        self.assertRedirects(response, expected_url=expected_url)

    def test_authenticated_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_authenticated_private_worlds_are_listed_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(response, self.private_worlds[0].name)

    def test_authenticated_empty_private_worlds_ok(self):
        # NOTE: We can work around this with a new user since it won't have any worlds
        user = baker.make_recipe('registration.user')
        self.client.force_login(user)
        response = self.client.get(self.url)

        self.assertContains(response, 'Seems like you haven\'t any world.')

    def test_authenticated_empty_community_worlds_ok(self):
        [place.delete() for place in self.public_worlds]
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(response, 'Seems like we don\'t have community worlds.')

    def test_authenticated_private_worlds_paginated_ok(self):
        generate_place(self.view.paginate_by, is_public=False, site_type=enums.SiteTypes.WORLD, owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_authenticated_public_worlds_paginated_ok(self):
        generate_place(self.view.paginate_by, is_public=True, site_type=enums.SiteTypes.WORLD)
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_authenticated_place_without_description_ok(self):
        self.public_worlds[0].description = ''
        self.public_worlds[0].save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    # NOTE: These two tests are dumps since `common/include/paginator.html` does not have tests
    def test_pagination_has_previous_and_next_ok(self):
        generate_place(self.view.paginate_by * 3, is_public=True, site_type=enums.SiteTypes.WORLD)
        self.client.force_login(self.user)
        response = self.client.get(f'{self.url}?page=2')

        self.assertEqual(200, response.status_code)

    def test_pagination_has_not_next_ok(self):
        generate_place(self.view.paginate_by * 2, is_public=True, site_type=enums.SiteTypes.WORLD)
        self.client.force_login(self.user)
        response = self.client.get(f'{self.url}?page=last')

        self.assertEqual(200, response.status_code)


class TestWorldCreateView(TestCase):
    model = Place
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:world:create'
    template = 'roleplay/world/world_create.html'
    url = resolve_url(resolver)

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user: User = baker.make_recipe('registration.user')

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.tmp_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        Image.new('RGB', (30, 60), color='red').save(cls.tmp_file.name)
        with open(cls.tmp_file.name, 'rb') as img_content:
            cls.image = SimpleUploadedFile(
                name=cls.tmp_file.name, content=img_content.read(), content_type='image/jpeg',
            )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.tmp_file.close()
        os.unlink(cls.tmp_file.name)

    def setUp(self) -> None:
        self.data = {
            'name': fake.sentence(nb_words=3),
            'description': fake.paragraph(),
            'image': self.image,
        }

    def test_access_anonymous_user_ko(self):
        response = self.client.get(self.url)
        expected_url = '{login_url}?next={url}'.format(login_url=self.login_url, url=self.url)

        self.assertRedirects(response, expected_url)

    def test_access_authenticated_ok(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_authenticated_template_is_ok(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_access_authenticated_with_user_in_kwargs_ok(self):
        self.client.force_login(self.user)

        response = self.client.get(f'{self.url}?user')

        self.assertEqual(200, response.status_code)

    def test_access_authenticated_create_world_without_name_ko(self):
        self.client.force_login(self.user)
        data_without_name = self.data.copy()
        del data_without_name['name']

        response = self.client.post(self.url, data=data_without_name)

        self.assertFormError(response.context['form'], 'name', 'This field is required.')

    def test_access_authenticated_create_world_without_description_ok(self):
        self.client.force_login(self.user)
        data_without_description = self.data.copy()
        del data_without_description['description']

        self.client.post(self.url, data=data_without_description, follow=True)

        self.assertTrue(len(self.user.accessible_places()) == 1)

    def test_access_authenticated_create_world_without_image_ok(self):
        self.client.force_login(self.user)
        data_without_image = self.data.copy()
        del data_without_image['image']

        self.client.post(self.url, data=data_without_image, follow=True)

        self.assertTrue(len(self.user.accessible_places()) == 1)


class TestWorldUpdateView(TestCase):
    model = Place
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:world:edit'
    template = 'roleplay/place/place_update.html'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user: User = baker.make_recipe('registration.user')

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.tmp_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        Image.new('RGB', (30, 60), color='red').save(cls.tmp_file.name)
        with open(cls.tmp_file.name, 'rb') as img_content:
            cls.image = SimpleUploadedFile(
                name=cls.tmp_file.name, content=img_content.read(), content_type='image/jpeg',
            )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.tmp_file.close()
        os.unlink(cls.tmp_file.name)

    def setUp(self) -> None:
        self.world: Place = generate_place(owner=self.user)
        self.url = resolve_url(self.resolver, pk=self.world.pk)
        self.data = {
            'name': fake.sentence(nb_words=3),
            'description': fake.paragraph(),
            'image': self.image,
        }

    def test_access_anonymous_user_ko(self):
        response = self.client.get(self.url)
        expected_url = '{login_url}?next={url}'.format(login_url=self.login_url, url=self.url)

        self.assertRedirects(response, expected_url)

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_template_used_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_private_world_remains_private_after_update_ok(self):
        """
        This tests comes from the bug that happened twice about Worlds becoming `public` when performing update.
        It's more defensive programming than a functional test itself.
        """

        self.world.is_public = False
        self.world.save(update_fields=['is_public'])

        self.client.force_login(self.user)
        self.client.post(path=self.url, data=self.data)
        self.world.refresh_from_db()

        self.assertFalse(self.world.is_public)

    def test_public_world_remains_public_after_update_ok(self):
        """
        This test is the counter-part to `test_private_world_remains_private_after_update_ok`.
        """

        self.world.is_public = True
        self.world.save(update_fields=['is_public'])

        self.client.force_login(self.user)
        self.client.post(path=self.url, data=self.data)
        self.world.refresh_from_db()

        self.assertTrue(self.world.is_public)


class TestCampaignCreateView(TestCase):
    model = Campaign
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:campaign:create'
    template = 'roleplay/campaign/campaign_create.html'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.world = generate_place(is_public=True, site_type=enums.SiteTypes.WORLD)
        cls.url = resolve_url(cls.resolver, world_pk=cls.world.pk)

    def setUp(self):
        self.data_ok = {
            'place': self.world.pk,
            'name': fake.sentence(nb_words=2),
            'system': random.choice(enums.RoleplaySystems.values),
        }

    def test_access_anonymous_user_ko(self):
        response = self.client.get(self.url)
        expected_url = '{login_url}?next={url}'.format(login_url=self.login_url, url=self.url)

        self.assertRedirects(response, expected_url)

    def test_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_template_used_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'roleplay/campaign/campaign_create.html')

    def test_non_existent_world_ko(self):
        self.client.force_login(self.user)
        non_existent_pk = Place.objects.last().pk + 1
        url = reverse('roleplay:campaign:create', kwargs={'world_pk': non_existent_pk})
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_creates_campaign_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.data_ok)
        campaign = Campaign.objects.get(owner__pk=self.user.pk)

        self.assertEqual(self.data_ok['name'], campaign.name)
        self.assertEqual(self.data_ok['system'], campaign.system)
        self.assertEqual(self.user, campaign.owner)
        self.assertEqual(self.world, campaign.place)

    def test_game_master_is_added_to_chat_ok(self):
        self.client.force_login(self.user)
        self.client.post(path=self.url, data=self.data_ok)
        campaign = Campaign.objects.get(owner__pk=self.user.pk)

        self.assertIn(self.user, campaign.chat.users.all())

    def test_bot_is_added_to_chat_ok(self):
        self.client.force_login(self.user)
        self.client.post(path=self.url, data=self.data_ok)
        campaign = Campaign.objects.get(owner__pk=self.user.pk)
        bot = User.get_bot()

        self.assertIn(bot, campaign.chat.users.all())

    def test_email_invitations_are_sent_ok(self):
        data = self.data_ok.copy()
        n_emails = 3
        emails = [fake.email() for _ in range(n_emails)]
        data['email_invitations'] = '\n'.join(emails)
        self.client.force_login(self.user)
        self.client.post(self.url, data=data)

        # NOTE: Since is asynchronous, we need to wait for the email to be sent
        time.sleep(1)
        self.assertEqual(len(mail.outbox), n_emails)
        self.assertEqual(mail.outbox[0].subject, 'A quest for you!')


class TestCampaignJoinView(TestCase):
    model = Campaign
    resolver = 'roleplay:campaign:join'

    @classmethod
    def setUpTestData(cls):
        cls.user: User = baker.make_recipe('registration.user')
        cls.instance: Campaign = baker.make_recipe('roleplay.campaign')
        cls.signer = TimestampSigner()

    def test_access_with_correct_token_and_existing_user_ok(self):
        token = tools.get_token(self.user.email, self.signer)
        url = resolve_url(self.resolver, pk=self.instance.pk, token=token)
        response = self.client.get(url)

        self.assertRedirects(response, resolve_url(self.instance), target_status_code=302)

    @patch('roleplay.views.messages')
    def test_access_with_correct_token_and_existing_user_messages_ok(self, mock_messages):
        token = tools.get_token(self.user.email, self.signer)
        url = resolve_url(self.resolver, pk=self.instance.pk, token=token)
        response = self.client.get(url)

        mock_messages.success.assert_called_once_with(response.wsgi_request, 'You have joined the campaign.')

    def test_access_with_correct_token_and_non_existing_user_redirects_to_login_ko(self):
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.instance.pk, token=token)
        response = self.client.get(url)

        self.assertRedirects(response, resolve_url(settings.LOGIN_URL))

    @patch('roleplay.views.messages')
    def test_access_with_correct_token_and_non_existing_user_messages_ko(self, mock_messages):
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.instance.pk, token=token)
        response = self.client.get(url)

        mock_messages.warning.assert_called_once_with(
            response.wsgi_request,
            'You need an account to join this campaign.'
        )

    def test_access_with_logged_user_ok(self):
        self.client.force_login(self.user)
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.instance.pk, token=token)
        response = self.client.get(url)

        self.assertRedirects(response, resolve_url(self.instance))

    def test_access_with_logged_user_adds_user_to_players_ok(self):
        self.client.force_login(self.user)
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.instance.pk, token=token)
        self.client.get(url)

        self.assertIn(self.user, self.instance.users.all())

    def test_access_with_incorrect_token_ko(self):
        token = f'{fake.email()}:{fake.password()}'
        url = resolve_url(self.resolver, pk=self.instance.pk, token=token)
        response = self.client.get(url)

        self.assertEqual(404, response.status_code)

    def test_users_are_added_to_chat_ok(self):
        self.client.force_login(self.user)
        token = tools.get_token(fake.email(), self.signer)
        url = resolve_url(self.resolver, pk=self.instance.pk, token=token)
        self.client.get(url)

        self.assertIn(self.user, self.instance.chat.users.all())


class TestCampaignLeaveView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:campaign:leave'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.instance: Campaign = baker.make_recipe('roleplay.campaign')
        cls.url = resolve_url(cls.resolver, pk=cls.instance.pk)

    def setUp(self) -> None:
        self.user: User = baker.make_recipe('registration.user')
        self.instance.users.add(self.user)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_user_not_in_campaign_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.url)

        self.assertEqual(404, response.status_code)

    def test_access_user_in_campaign_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        expected_url = resolve_url('roleplay:campaign:list')

        self.assertRedirects(response=response, expected_url=expected_url)

    @patch('roleplay.views.messages')
    def test_user_gets_success_message_ok(self, mock_messages: MagicMock):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        mock_messages.success.assert_called_once_with(
            response.wsgi_request,
            'You have left the campaign.'
        )

    def test_user_is_removed_from_campaign_ok(self):
        self.client.force_login(self.user)
        self.client.get(self.url)

        self.assertNotIn(self.user, self.instance.users.all())

    def test_user_is_removed_from_campaign_chat_ok(self):
        self.client.force_login(self.user)
        self.client.get(self.url)

        self.assertNotIn(self.user, self.instance.chat.users.all())


class TestCampaignRemovePlayerView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:campaign:remove-player'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.game_master: User = baker.make_recipe('registration.user')
        cls.instance: Campaign = baker.make_recipe('roleplay.campaign')
        cls.instance.add_game_masters(cls.game_master)

    def setUp(self) -> None:
        self.player: User = baker.make_recipe('registration.user')
        self.instance.users.add(self.player)
        self.url = resolve_url(self.resolver, pk=self.instance.pk, user_pk=self.player.pk)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_user_not_in_campaign_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.url)

        self.assertEqual(404, response.status_code)

    def test_access_player_is_not_game_master_ko(self):
        self.client.force_login(self.player)
        response = self.client.get(self.url)

        self.assertEqual(404, response.status_code)

    def test_access_player_is_game_master_ok(self):
        self.client.force_login(self.game_master)
        response = self.client.get(self.url)
        expected_url = resolve_url(self.instance)

        self.assertRedirects(response=response, expected_url=expected_url)

    @patch('roleplay.views.messages')
    def test_user_gets_success_message_ok(self, mock_messages: MagicMock):
        self.client.force_login(self.game_master)
        response = self.client.get(self.url)

        mock_messages.success.assert_called_once_with(
            request=response.wsgi_request,
            message=f'You have removed {self.player.username} from campaign.',
        )

    def test_player_is_removed_from_campaign_ok(self):
        self.client.force_login(self.game_master)
        self.client.get(self.url)

        self.assertNotIn(self.player, self.instance.users.all())

    def test_player_is_removed_from_campaign_chat_ok(self):
        self.client.force_login(self.game_master)
        self.client.get(self.url)
        chat: Chat = self.instance.chat

        self.assertNotIn(self.player, chat.users.all())


class TestCampaignListView(TestCase):
    model = Campaign
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:campaign:list'
    template = 'roleplay/campaign/campaign_list.html'
    view = views.CampaignListView

    @classmethod
    def setUpTestData(cls):
        cls.url = resolve_url(cls.resolver)
        cls.user = baker.make_recipe('registration.user')

    def test_anonymous_access_ok(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_user_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_template_used_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_private_campaigns_are_not_listed_ok(self):
        self.client.force_login(self.user)
        campaign = baker.make_recipe('roleplay.campaign', is_public=False)
        response = self.client.get(self.url)

        self.assertNotIn(campaign, response.context['campaign_list'])

    def test_public_campaigns_are_listed_ok(self):
        self.client.force_login(self.user)
        campaign = baker.make_recipe('roleplay.public_campaign')
        # We also get to create some campaign with image and description to complete coverage
        baker.make_recipe('roleplay.public_campaign', description=fake.paragraph())
        baker.make_recipe('roleplay.public_campaign', cover_image=fake.file_name(category='image'))
        # We also create a session in order to get last session footer
        baker.make_recipe('roleplay.session', campaign=campaign, next_game=fake.past_date())
        response = self.client.get(self.url)

        self.assertIn(campaign, response.context['campaign_list'])

    @pytest.mark.coverage
    def test_public_campaigns_with_pagination_ok(self):
        self.client.force_login(self.user)
        baker.make_recipe('roleplay.public_campaign', self.view.paginate_by)
        self.client.get(self.url)

    @pytest.mark.coverage
    def test_campaign_with_user_voted_positive_ok(self):
        self.client.force_login(self.user)
        campaign = baker.make_recipe('roleplay.public_campaign')
        baker.make(
            _model=Vote,
            is_positive=True,
            user=self.user,
            content_type=ContentType.objects.get_for_model(campaign),
            object_id=campaign.pk,
        )
        response = self.client.get(self.url)

        self.assertContains(response, 'btn btn-success disabled')

    @pytest.mark.coverage
    def test_campaign_with_user_voted_negative_ok(self):
        self.client.force_login(self.user)
        campaign = baker.make_recipe('roleplay.public_campaign')
        baker.make(
            _model=Vote,
            is_positive=False,
            user=self.user,
            content_type=ContentType.objects.get_for_model(campaign),
            object_id=campaign.pk,
        )
        response = self.client.get(self.url)

        self.assertContains(response, 'btn btn-danger disabled')

    def test_query_performance_ok(self):
        rq = RequestFactory()
        get_rq = rq.get(self.url)
        get_rq.user = self.user
        performed_queries = (
            'SELECT [...] FROM roleplay_campaign COMPLEX',
        )

        with self.assertNumQueries(len(performed_queries)):
            self.view.as_view()(get_rq)


class TestCampaignUserListView(TestCase):
    model = Campaign
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:campaign:list-private'
    template = 'roleplay/campaign/campaign_private_list.html'
    view = views.CampaignUserListView

    @classmethod
    def setUpTestData(cls):
        cls.url = resolve_url(cls.resolver)
        cls.user = baker.make_recipe('registration.user')

    def setUp(self):
        # NOTE: max_value is set to pagination_by in order to get a "full" pagination
        self.n_owned_campaigns = fake.pyint(min_value=1, max_value=self.view.paginate_by)
        owned_campaigns = baker.make_recipe('roleplay.campaign', _quantity=self.n_owned_campaigns, owner=self.user)
        [campaign.users.add(self.user) for campaign in owned_campaigns]
        # Random campaigns
        baker.make_recipe('roleplay.campaign', _quantity=fake.pyint(min_value=1, max_value=10))

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_user_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_templated_used_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_listed_campaigns_for_user_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        campaigns = response.context['object_list']

        self.assertEqual(len(campaigns), self.n_owned_campaigns)

    def test_query_performance_ok(self):
        rq = RequestFactory()
        get_rq = rq.get(self.url)
        get_rq.user = self.user
        performed_queries = (
            'SELECT [...] FROM roleplay_campaign COMPLEX',
        )

        with self.assertNumQueries(len(performed_queries)):
            self.view.as_view()(get_rq)

    @pytest.mark.coverage
    def test_empty_campaigns_ok(self):
        self.model.objects.all().delete()
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(response, 'Go to \'Worlds\' and click \'Create Campaign\' to create one.')


class TestCampaignUpdateView(TestCase):
    model = Campaign
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:campaign:edit'
    template = 'roleplay/campaign/campaign_update.html'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.world = generate_place(is_public=True, site_type=enums.SiteTypes.WORLD)

    def setUp(self):
        self.campaign_user_is_not_gm = baker.make_recipe('roleplay.campaign', owner=self.user, place=self.world)
        self.campaign_not_gm_url = reverse(self.resolver, kwargs={'pk': self.campaign_user_is_not_gm.pk})
        self.campaign = baker.make_recipe('roleplay.campaign', owner=self.user, place=self.world)
        self.campaign.add_game_masters(self.user)
        self.url = reverse(self.resolver, kwargs={'pk': self.campaign.pk})

        self.new_name = fake.sentence(nb_words=2)
        self.data_ok = {
            'name': self.new_name,
            'system': self.campaign.system,
            'place': self.campaign.place.pk,
        }

    def test_anonymous_access_ko(self):
        response = self.client.get(self.campaign_not_gm_url)
        expected_url = f'{self.login_url}?next={self.campaign_not_gm_url}'

        self.assertRedirects(response, expected_url)

    def test_user_not_in_users_access_ko(self):
        self.client.force_login(self.user)
        response = self.client.get(self.campaign_not_gm_url)

        self.assertEqual(403, response.status_code)

    def test_user_in_users_not_game_master_access_ko(self):
        self.campaign_user_is_not_gm.users.add(self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.campaign_not_gm_url)

        self.assertEqual(403, response.status_code)

    def test_user_in_users_game_master_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_templated_used_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_campaign_is_changed_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.data_ok)
        self.campaign.refresh_from_db()

        self.assertEqual(self.new_name, self.campaign.name)

    def test_post_data_does_not_change_owner_ok(self):
        self.another_user = baker.make_recipe('registration.user')
        self.campaign.add_game_masters(self.another_user)
        self.client.force_login(self.another_user)
        self.client.post(self.url, data=self.data_ok)
        self.campaign.refresh_from_db()

        self.assertEqual(self.user, self.campaign.owner)

    def test_redirect_to_campaign_detail_ok(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.data_ok)

        self.assertRedirects(response, resolve_url(self.campaign))

    def test_email_invitations_are_sent_ok(self):
        data = self.data_ok.copy()
        n_emails = 3
        emails = [fake.email() for _ in range(n_emails)]
        data['email_invitations'] = '\n'.join(emails)
        self.client.force_login(self.user)
        self.client.post(self.url, data=data)

        # NOTE: Since is asynchronous, we need to wait for the email to be sent
        time.sleep(1)
        self.assertEqual(len(mail.outbox), n_emails)
        self.assertEqual(mail.outbox[0].subject, 'A quest for you!')


class TestCampaignDetailView(TestCase):
    model = Campaign
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:campaign:detail'
    template = 'roleplay/campaign/campaign_detail.html'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.world = generate_place(site_type=enums.SiteTypes.WORLD)

    def setUp(self):
        self.private_campaign: Campaign = baker.make_recipe('roleplay.private_campaign', place=self.world)
        self.private_campaign.users.add(self.user)
        self.private_campaign_url = resolve_url(self.private_campaign)
        self.public_campaign: Campaign = baker.make_recipe('roleplay.public_campaign', place=self.world)
        self.public_campaign_url = resolve_url(self.public_campaign)

    def test_access_anonymous_ko(self):
        response = self.client.get(self.private_campaign_url)
        expected_url = f'{self.login_url}?next={self.private_campaign_url}'

        self.assertRedirects(response, expected_url)

    def test_user_not_in_players_private_campaign_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.private_campaign_url)

        self.assertEqual(403, response.status_code)

    def test_user_in_players_private_campaign_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.private_campaign_url)

        self.assertEqual(200, response.status_code)

    def test_user_not_in_players_public_campaign_ok(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.public_campaign_url)

        self.assertEqual(200, response.status_code)

    def test_user_is_owner_of_campaign_ok(self):
        campaign = baker.make_recipe('roleplay.campaign', owner=self.user)
        url = resolve_url(campaign)
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_template_used_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.private_campaign_url)

        self.assertTemplateUsed(response, self.template)

    @patch('roleplay.views.messages')
    def test_request_join_ok(self, mocker):
        self.client.force_login(self.user)
        response = self.client.post(self.private_campaign_url)

        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'You\'ve requested to join this adventure. Once the GMs accepts your request, you\'ll receive an email.',
        )
        self.assertRedirects(response, self.private_campaign_url)

    def test_email_sent_ok(self):
        self.private_campaign.add_game_masters(baker.make_recipe('registration.user'))
        self.client.force_login(self.user)
        self.client.post(self.private_campaign_url)

        time.sleep(1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'New player wants to join your adventure!')

    @pytest.mark.coverage
    def test_campaign_with_image_and_other_fields_ok(self):
        # NOTE: start_date, end_date, summary
        self.client.force_login(self.user)
        self.private_campaign.summary = fake.sentence()
        self.private_campaign.description = fake.paragraph()
        self.private_campaign.cover_image = fake.file_name(category='image')
        self.private_campaign.start_date = fake.date_time_this_year()
        self.private_campaign.end_date = fake.past_datetime()
        self.private_campaign.save()
        response = self.client.get(self.private_campaign_url)

        self.assertContains(response, self.private_campaign.cover_image.url)

    @pytest.mark.coverage
    def test_campaign_with_complex_place_ok(self):
        self.client.force_login(self.user)
        place_with_child = generate_place(level=1, parent_site=self.world)
        place_with_child.children_sites.add(generate_place(level=2))
        response = self.client.get(self.private_campaign_url)

        self.assertContains(response, place_with_child.name)

    @pytest.mark.coverage
    def test_campaign_with_sessions_ok(self):
        self.client.force_login(self.user)
        session = baker.make_recipe('roleplay.session', campaign=self.private_campaign)
        response = self.client.get(self.private_campaign_url)

        self.assertContains(response, session.name)

    @pytest.mark.coverage
    def test_campaign_with_game_masters_ok(self):
        gm = baker.make_recipe('registration.user')
        self.client.force_login(gm)
        self.private_campaign.add_game_masters(gm)
        response = self.client.get(self.private_campaign_url)

        self.assertContains(response, 'General settings')
        self.assertContains(response, resolve_url('roleplay:campaign:edit', pk=self.private_campaign.pk))

    @pytest.mark.coverage
    def test_campaign_with_player_with_profile_image_ok(self):
        self.client.force_login(self.user)
        user_with_profile_image = baker.make_recipe('registration.user')
        profile_with_image = user_with_profile_image.profile
        profile_with_image.image = fake.file_name(category='image')
        profile_with_image.save(update_fields=['image'])
        self.private_campaign.users.add(user_with_profile_image)
        response = self.client.get(self.private_campaign_url)

        self.assertContains(response, user_with_profile_image.profile.image.url)

    @pytest.mark.coverage
    @patch('bot.utils.discord_api_request')
    def test_campaign_with_discord_channel_ok(self, mocker_api_request: MagicMock):
        discord_channel_id = f'{fake.random_number(digits=18)}'
        mocker_api_request.return_value = discord.channel_response(id=discord_channel_id)

        self.client.force_login(self.user)
        self.private_campaign.discord_channel_id = discord_channel_id
        self.private_campaign.save(update_fields=['discord_channel_id'])
        response = self.client.get(self.private_campaign_url)
        discord_guild_id = self.private_campaign.discord_channel.guild_id
        discord_channel_url = f'https://discord.com/channels/{discord_guild_id}/{discord_channel_id}'

        self.assertContains(response, discord_channel_url)

    def test_user_sees_leave_button_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.private_campaign_url)

        self.assertContains(response=response, text='Leave')

    def test_player_dont_see_create_session_button_in_campaign_with_sessions_ok(self):
        baker.make_recipe('roleplay.session', campaign=self.private_campaign)
        self.client.force_login(self.user)
        response = self.client.get(self.private_campaign_url)

        self.assertNotContains(response=response, text='Create session')

    def test_game_master_sees_create_session_button_in_campaign_with_sessions_ok(self):
        baker.make_recipe('roleplay.session', campaign=self.private_campaign)
        gm = baker.make_recipe('registration.user')
        self.private_campaign.add_game_masters(gm)
        self.client.force_login(gm)
        response = self.client.get(self.private_campaign_url)

        self.assertContains(response=response, text='Create session')


class TestCampaignDeleteView(TestCase):
    model = Campaign
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:campaign:delete'
    template = 'roleplay/campaign/campaign_confirm_delete.html'

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.world = baker.make_recipe('roleplay.world')
        cls.campaign = baker.make_recipe('roleplay.campaign', owner=cls.user, place=cls.world)
        cls.url = resolve_url(cls.resolver, pk=cls.campaign.pk)

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_user_not_owner_access_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.url)

        self.assertEqual(403, response.status_code)

    def test_user_owner_access_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_template_used_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_campaign_is_deleted_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url)

        self.assertFalse(Campaign.objects.filter(pk=self.campaign.pk).exists())

    @patch('roleplay.views.messages')
    def test_success_message_sent_ok(self, mocker):
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        mocker.success.assert_called_once_with(
            response.wsgi_request,
            'Campaign deleted successfully.',
        )


class TestSessionCreateView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = Session
    resolver = 'roleplay:session:create'
    template = 'roleplay/session/session_create.html'
    view = views.SessionCreateView

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.campaign = baker.make_recipe('roleplay.campaign')
        cls.campaign.add_game_masters(cls.user)

    def setUp(self):
        self.url = resolve_url(self.resolver, campaign_pk=self.campaign.pk)
        self.data_ok = {
            'name': fake.sentence(),
            'description': fake.paragraph(),
            'plot': fake.sentence(nb_words=4),
            'gm_info': fake.paragraph(),
            'next_game': fake.future_datetime(),
        }

    def test_access_anonymous_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_non_game_master_ko(self):
        self.client.force_login(baker.make_recipe('registration.user'))
        response = self.client.get(self.url)

        self.assertEqual(404, response.status_code)

    def test_access_logged_user_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_template_used_is_correct_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_post_data_without_name_ko(self):
        data_without_name = self.data_ok.copy()
        del data_without_name['name']

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_without_name)

        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_post_data_next_game_in_the_past_ko(self):
        data_with_past_next_game = self.data_ok.copy()
        data_with_past_next_game['next_game'] = fake.past_datetime()

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=data_with_past_next_game)

        self.assertFormError(response, 'form', 'next_game', 'Next game date must be in the future.')

    def test_post_data_redirect_ok(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.data_ok)
        session_created = self.model.objects.order_by('entry_created_at').last()

        self.assertRedirects(response, resolve_url(session_created))


class TestSessionDetailView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = Session
    resolver = 'roleplay:session:detail'
    template = 'roleplay/session/session_detail.html'
    view = views.SessionDetailView

    @classmethod
    def setUpTestData(cls):
        cls.user_in_players = baker.make_recipe('registration.user')
        cls.user_not_in_players = baker.make_recipe('registration.user')
        cls.campaign = baker.make_recipe('roleplay.campaign', users=[cls.user_in_players])

        cls.session = baker.make_recipe('roleplay.session', campaign=cls.campaign)
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
        self.session.campaign.users.add(user)
        self.client.force_login(user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_with_game_master_ok(self):
        session = baker.make_recipe('roleplay.session')
        session.campaign.add_game_masters(self.user_in_players)
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
    model = Session
    resolver = 'roleplay:session:delete'
    template = 'roleplay/session/session_confirm_delete.html'
    view = views.SessionDeleteView

    @classmethod
    def setUpTestData(cls):
        cls.user_in_game_masters = baker.make_recipe('registration.user')
        cls.user_not_in_game_masters = baker.make_recipe('registration.user')
        cls.campaign = baker.make_recipe('roleplay.campaign')
        cls.campaign.add_game_masters(cls.user_in_game_masters)

        cls.session = baker.make_recipe('roleplay.session', campaign=cls.campaign)
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

    @patch('roleplay.views.messages')
    def test_access_game_master_session_deleted_message_ok(self, mock_messages):
        self.client.force_login(self.user_in_game_masters)
        response = self.client.post(self.url)

        mock_messages.success.assert_called_once_with(
            response.wsgi_request,
            'Session deleted.',
        )


class TestSessionUpdateView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = Session
    resolver = 'roleplay:session:edit'
    template = 'roleplay/session/session_update.html'
    view = views.SessionUpdateView

    @classmethod
    def setUpTestData(cls):
        cls.user_in_game_masters = baker.make_recipe('registration.user')
        cls.user_not_in_game_masters = baker.make_recipe('registration.user')
        cls.campaign = baker.make_recipe('roleplay.campaign')
        cls.campaign.add_game_masters(cls.user_in_game_masters)

        cls.session = baker.make_recipe('roleplay.session', campaign=cls.campaign)
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
            'next_game': self.session.next_game,
            'campaign': self.session.campaign.pk,
        }
        self.client.force_login(self.user_in_game_masters)
        self.client.post(self.url, data)
        self.session.refresh_from_db()

        self.assertEqual(name, self.session.name)

    @patch('roleplay.views.messages')
    def test_access_game_master_session_updated_message_ok(self, mock_messages):
        data = {
            'name': fake.sentence(),
            'plot': fake.text(),
            'next_game': self.session.next_game,
            'campaign': self.session.campaign.pk,
        }
        self.client.force_login(self.user_in_game_masters)
        response = self.client.post(self.url, data)

        mock_messages.success.assert_called_once_with(
            response.wsgi_request,
            'Session updated!'
        )


class TestSessionListView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = Session
    resolver = 'roleplay:session:list'
    template = 'roleplay/session/session_list.html'
    view = views.SessionListView

    @classmethod
    def setUpTestData(cls):
        cls.url = resolve_url(cls.resolver)

        cls.user = baker.make_recipe('registration.user')
        profile = cls.user.profile
        profile.image = fake.file_name(category='image')
        profile.save(update_fields=['image'])
        cls.another_user = baker.make_recipe('registration.user')

        baker.make_recipe(
            baker_recipe_name='roleplay.session',
            _quantity=fake.pyint(min_value=1, max_value=cls.view.paginate_by),
            campaign=baker.make_recipe('roleplay.campaign', users=[cls.user, cls.another_user]),
        )

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

        self.assertEqual(self.user.sessions.count(), response.context['object_list'].count())

    def test_access_session_with_image_ok(self):
        session = baker.make_recipe(
            'roleplay.session',
            campaign=baker.make_recipe('roleplay.campaign', users=[self.user])
        )
        session.image = SimpleUploadedFile('image.png', b'file_content', content_type='image/png')
        session.save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_access_session_list_only_where_user_is_player_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        baker.make_recipe('roleplay.session', _quantity=fake.pyint(min_value=1, max_value=10))

        self.assertEqual(self.user.sessions.count(), response.context['object_list'].count())

    def test_access_session_list_with_more_than_three_players_ok(self):
        self.client.force_login(self.user)

        session = baker.make_recipe(
            'roleplay.session',
            campaign=baker.make_recipe('roleplay.campaign')
        )
        session.campaign.users.add(self.user, *baker.make_recipe('registration.user', _quantity=3))
        response = self.client.get(self.url)
        expected_in_html = 'and 1 more player...'

        self.assertContains(response=response, text=expected_in_html)

    def test_access_session_list_with_more_than_four_players_ok(self):
        self.client.force_login(self.user)

        session = baker.make_recipe(
            'roleplay.session',
            campaign=baker.make_recipe('roleplay.campaign')
        )
        session.campaign.users.add(self.user, *baker.make_recipe('registration.user', _quantity=4))
        response = self.client.get(self.url)
        expected_in_html = 'and 2 more players...'

        self.assertContains(response=response, text=expected_in_html)

    def test_query_performance_ok(self):
        rq = RequestFactory().get(self.url)
        rq.user = self.user
        queries = (
            'SELECT [...] FROM roleplay.session',
        )

        with self.assertNumQueries(len(queries)):
            self.view.as_view()(rq)


@unittest.skip('WIP: OAR-18')
class TestRaceCreateView(TestCase):
    login_url = reverse('registration:auth:login')
    model = Race
    resolver = 'roleplay:race:create'
    template = 'roleplay/race/race_create.html'
    view = views.RaceCreateView

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.race = baker.make(Race)

    def setUp(self):
        self.users = baker.make('registration.user')
        self.url = reverse(self.resolver)
        self.data_ok = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'strength': fake.random_int(min=-5, max=5),
            'dexterity': fake.random_int(min=-5, max=5),
            'charisma': fake.random_int(min=-5, max=5),
            'constitution': fake.random_int(min=-5, max=5),
            'intelligence': fake.random_int(min=-5, max=5),
            'affected_by_armor': fake.boolean(),
            'wisdom': fake.random_int(min=-5, max=5),
            'image': fake.image_url(),
            'users': [self.user.pk]
        }

    def test_access_templated_used_is_correct_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_creates_race_ok(self):
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.data_ok)
        instance = self.model.objects.first()

        self.assertEqual(self.data_ok['name'], instance.name)
        self.assertEqual(self.data_ok['description'], instance.description)


@unittest.skip('WIP: OAR-18')
class TestRaceDetailView(TestCase):
    model = Race
    resolver = 'roleplay:place:detail'
    template = 'roleplay/race/race_detail.html'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.users = baker.make_recipe('registration.user')
        cls.race = baker.make_recipe('roleplay.race')
        cls.race_without_optional = baker.make_recipe('roleplay.race_without_optional')

        cls.race.users.add(cls.users)
        cls.race_without_optional.users.add(cls.users)

        cls.owner = cls.users

        cls.url = reverse('roleplay:race:detail', kwargs={'pk': cls.race.pk})
        cls.url_without_optional = reverse('roleplay:race:detail', kwargs={'pk': cls.race_without_optional.pk})

    def test_access_template_used_is_correct_ok(self):
        self.client.force_login(self.users)
        response = self.client.get(self.url, kwargs={'pk': self.race.pk})

        self.assertTemplateUsed(response, self.template)

    def test_without_optional_template_used_is_correct_ok(self):
        self.client.force_login(self.users)
        response = self.client.get(self.url_without_optional, kwargs={'pk': self.race_without_optional.pk})

        self.assertTemplateUsed(response, self.template)


@unittest.skip('WIP: OAR-18')
class TestRaceUpdateView(TestCase):
    model = Race
    resolver = 'roleplay:place:edit'
    template = 'roleplay/race/race_update.html'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.users = baker.make_recipe('registration.user')

        cls.race = cls.model.objects.create(
            name=fake.word(),
            description=fake.paragraph(),
            strength=fake.random_int(min=-5, max=5),
            dexterity=fake.random_int(min=-5, max=5),
            charisma=fake.random_int(min=-5, max=5),
            constitution=fake.random_int(min=-5, max=5),
            intelligence=fake.random_int(min=-5, max=5),
            affected_by_armor=fake.boolean(),
            wisdom=fake.random_int(min=-5, max=5),
            image=fake.image_url(),
        )
        cls.race.users.add(cls.users)
        cls.owner = cls.users

        cls.url = reverse('roleplay:race:edit', kwargs={'pk': cls.race.pk})

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        Image.new('RGB', (30, 60), color='red').save(self.tmp_file.name)
        with open(self.tmp_file.name, 'rb') as img_content:
            image = SimpleUploadedFile(name=self.tmp_file.name, content=img_content.read(), content_type='image/jpeg')

        self.data_ok = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'strength': fake.random_int(min=-5, max=5),
            'dexterity': fake.random_int(min=-5, max=5),
            'charisma': fake.random_int(min=-5, max=5),
            'constitution': fake.random_int(min=-5, max=5),
            'intelligence': fake.random_int(min=-5, max=5),
            'affected_by_armor': fake.boolean(),
            'wisdom': fake.random_int(min=-5, max=5),
            'image': image,
            'users': [self.users.pk]
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
        self.client.force_login(self.users)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)

    def test_anonymous_post_data_ko(self):
        login_url = reverse('registration:auth:login')
        response = self.client.post(self.url, data=self.data_ok)

        self.assertRedirects(response, f'{login_url}?next={self.url}')

    def test_post_data_ok(self):
        self.client.force_login(self.owner)
        current_name = self.race.name
        new_name = self.data_ok['name']
        response = self.client.post(self.url, data=self.data_ok)
        self.race.refresh_from_db()

        self.assertRedirects(response, reverse('roleplay:race:detail', kwargs={'pk': self.race.pk}))
        self.assertNotEqual(current_name, new_name)
        self.assertEqual(self.race.name, new_name)


class TestRaceListView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    resolver = 'roleplay:race:list'
    template = 'roleplay/race/race_list.html'
    view = views.RaceListView

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.url = resolve_url(cls.resolver)

    def test_anonymous_access_ko(self):
        response = self.client.get(path=self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_logged_user_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertEqual(200, response.status_code)

    def test_access_templated_used_is_correct_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertTemplateUsed(response=response, template_name=self.template)

    def test_access_without_races_and_see_buttons_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertContains(response=response, text='Create race for world')
        self.assertContains(response=response, text='Create race for campaign')

    def test_access_with_races_and_sees_them_ok(self):
        race: Race = baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertContains(response=response, text=race.name)
        self.assertContains(response=response, text=race.description)

    def test_access_without_owned_races_and_does_not_see_others_races_ok(self):
        race: Race = baker.make_recipe('roleplay.race')
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertNotContains(response=response, text=race.name)
        self.assertNotContains(response=response, text=race.description)

    def test_advanced_search_is_displayed_if_there_are_any_races_ok(self):
        baker.make_recipe('roleplay.race', owner=self.user)

        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertContains(response=response, text='Advanced Search')

    def test_advanced_search_is_not_displayed_if_there_is_no_race_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertNotContains(response=response, text='Advanced Search')

    def test_create_for_buttons_are_displayed_if_there_is_no_race_ok(self):
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertContains(response=response, text='Create race for world')
        self.assertContains(response=response, text='Create race for campaign')

    def test_create_for_buttons_are_not_displayed_if_there_is_any_race_ok(self):
        baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertNotContains(response=response, text='Create race for world')
        self.assertNotContains(response=response, text='Create race for campaign')

    def test_search_by_name_with_existent_races_ok(self):
        race: Race = baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'name': race.name})

        self.assertContains(response=response, text=race.name)

    def test_search_by_name_with_non_existent_races_ok(self):
        baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'name': fake.word()})

        self.assertContains(response=response, text='There isn\'t any race with this characteristics.')
        self.assertContains(response=response, text='Remove filter or create one.')

    def test_search_by_description_with_existent_races_ok(self):
        race: Race = baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'description': race.description})

        self.assertContains(response=response, text=race.name)

    def test_search_by_description_with_non_existent_races_ok(self):
        baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'description': fake.word()})

        self.assertContains(response=response, text='There isn\'t any race with this characteristics.')
        self.assertContains(response=response, text='Remove filter or create one.')

    def test_search_by_campaign_with_existent_races_ok(self):
        race: Race = baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'campaign': race.campaign.name})

        self.assertContains(response=response, text=race.name)

    def test_search_by_campaign_with_non_existent_races_ok(self):
        baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'campaign': fake.word()})

        self.assertContains(response=response, text='There isn\'t any race with this characteristics.')
        self.assertContains(response=response, text='Remove filter or create one.')

    def test_search_by_place_with_existent_races_ok(self):
        race: Race = baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'place': race.place.name})

        self.assertContains(response=response, text=race.name)

    def test_search_by_place_with_non_existent_races_ok(self):
        baker.make_recipe('roleplay.race', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'place': fake.word()})

        self.assertContains(response=response, text='There isn\'t any race with this characteristics.')
        self.assertContains(response=response, text='Remove filter or create one.')

    def test_search_by_ability_modifiers_with_existent_races_ok(self):
        race: Race = baker.make_recipe('roleplay.race', owner=self.user, strength=1)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'ability_modifiers': 'strength'})

        self.assertContains(response=response, text=race.name)

    def test_search_by_ability_modifiers_with_non_existent_races_ok(self):
        baker.make_recipe('roleplay.race_without_modifiers', owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url, data={'ability_modifiers': 'strength'})

        self.assertContains(response=response, text='There isn\'t any race with this characteristics.')
        self.assertContains(response=response, text='Remove filter or create one.')

    def test_races_paginated_ok(self):
        baker.make_recipe('roleplay.race', self.view.paginate_by + 1, owner=self.user)
        self.client.force_login(self.user)
        response = self.client.get(path=self.url)

        self.assertContains(response=response, text='Next')


@unittest.skip('WIP: OAR-18')
class TestRaceDeleteView(TestCase):
    login_url = resolve_url(settings.LOGIN_URL)
    model = Race
    resolver = 'roleplay:race:delete'
    template = 'roleplay/race/race_confirm_delete.html'
    view = views.RaceDeleteView

    @classmethod
    def setUpTestData(cls):
        cls.users = baker.make_recipe('registration.user')
        cls.race = baker.make_recipe('roleplay.race')

        cls.race.users.add(cls.users)
        cls.owner = cls.users

        cls.url = reverse('roleplay:race:delete', kwargs={'pk': cls.race.pk})

    def test_anonymous_access_ko(self):
        response = self.client.get(self.url)
        expected_url = f'{self.login_url}?next={self.url}'

        self.assertRedirects(response, expected_url)

    def test_access_templated_used_is_correct_ok(self):
        self.client.force_login(self.users)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, self.template)

    def test_access_redirect_ok(self):
        self.client.force_login(self.users)
        response = self.client.post(self.url)

        self.assertRedirects(response, resolve_url('roleplay:race:list'))
