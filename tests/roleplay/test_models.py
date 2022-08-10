import os
import pathlib
import random
import tempfile
import unittest
from datetime import timedelta

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.utils import DataError, IntegrityError
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time
from model_bakery import baker

from common.constants import models as constants
from roleplay.enums import DomainTypes, RoleplaySystems, SiteTypes

from roleplay.models import Campaign, Domain, Place, PlayerInCampaign, Race, RaceUser, Session
from .. import fake
from ..bot.helpers.constants import CHANNEL, LITECORD_API_URL, LITECORD_TOKEN
from ..utils import check_litecord_connection, generate_place

User = apps.get_model(constants.REGISTRATION_USER)

connection_engine = connection.features.connection.settings_dict.get('ENGINE', None)


class TestDomain(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Domain

    def test_str_ok(self):
        domain = baker.make(self.model)
        domain_type = DomainTypes(domain.domain_type)
        self.assertEqual(str(domain), f'{domain.name} [{domain_type.label.title()}]')

    def test_ok(self):
        entries = fake.pyint(min_value=1, max_value=100)
        baker.make(self.model, entries)
        self.assertEqual(entries, self.model.objects.count())

    @freeze_time('2020-01-01')
    def test_image_upload_ok(self):
        tmpfile = tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', dir='./tests/', delete=False)
        image_file = tmpfile.name
        with open(tmpfile.name, 'rb') as image_data:
            image = SimpleUploadedFile(name=image_file, content=image_data.read(), content_type='image/jpeg')

        place = baker.make(self.model)
        place.image = image
        place.save()
        expected_path = '/media/roleplay/domain/2020/01/01/{}/{}'.format(place.pk, image.name)
        expected_path = pathlib.Path(expected_path)
        self.assertIn(str(expected_path), place.image.path)

        tmpfile.close()
        os.unlink(tmpfile.name)
        os.unlink(place.image.path)

    @unittest.skipIf('sqlite3' in connection_engine, 'SQLite takes Varchar as Text')
    def test_max_name_length_ko(self):
        name = fake.password(length=26)
        with self.assertRaises(DataError) as ex:
            self.model.objects.create(name=name)
        self.assertRegex(str(ex.exception), r'.*value too long.*')

    def test_name_none_ko(self):
        with self.assertRaises(IntegrityError) as ex:
            self.model.objects.create(name=None)
        self.assertRegex(str(ex.exception), r'.*(null|NULL).*(constraint|CONSTRAINT).*')

    def test_is_domain_ok(self):
        instance = baker.make(self.model, domain_type=DomainTypes.DOMAIN)
        self.assertTrue(instance.is_domain)

    def test_is_domain_ko(self):
        instance = baker.make(self.model, domain_type=DomainTypes.SUBDOMAIN)
        self.assertFalse(instance.is_domain)

    def test_is_subdomain_ok(self):
        instance = baker.make(self.model, domain_type=DomainTypes.SUBDOMAIN)
        self.assertTrue(instance.is_subdomain)

    def test_is_subdomain_ko(self):
        instance = baker.make(self.model, domain_type=DomainTypes.DOMAIN)
        self.assertFalse(instance.is_subdomain)


class TestPlace(TestCase):
    model = Place

    def test_str_ok(self):
        place = generate_place()
        self.assertEqual(str(place), place.name)

    def test_ok(self):
        entries = fake.pyint(min_value=1, max_value=100)
        generate_place(entries)
        self.assertEqual(entries, self.model.objects.count())

    @freeze_time('2020-01-01')
    def test_image_upload_ok(self):
        tmpfile = tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', dir='./tests/', delete=False)
        image_file = tmpfile.name
        with open(tmpfile.name, 'rb') as image_data:
            image = SimpleUploadedFile(name=image_file, content=image_data.read(), content_type='image/jpeg')

        place = generate_place()
        place.image = image
        place.save()
        expected_path = '/media/roleplay/place/2020/01/01/{}/{}'.format(place.pk, image.name)
        expected_path = pathlib.Path(expected_path)
        self.assertIn(str(expected_path), place.image.path)

        tmpfile.close()
        os.unlink(tmpfile.name)
        os.unlink(place.image.path)

    def test_images_ok(self):
        images = []

        for _ in range(0, 3):
            tmpfile = tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', dir='./tests/', delete=False)
            image_file = tmpfile.name
            with open(tmpfile.name, 'rb') as image_data:
                image = SimpleUploadedFile(name=image_file, content=image_data.read(), content_type='image/jpeg')
            images.append(image)

            tmpfile.close()
            os.unlink(tmpfile.name)

        parent = None
        for image in images:
            place = generate_place(name=fake.country(), parent_site=parent)
            place.image = image
            place.save()
            parent = place

        obj_images = self.model.objects.first().images
        self.assertEqual(len(images), len(obj_images))

        for place in self.model.objects.all():
            os.unlink(place.image.path)

    @unittest.skipIf('sqlite3' in connection_engine, 'SQLite takes Varchar as Text')
    def test_max_name_length_ko(self):
        name = fake.password(length=101)
        with self.assertRaises(DataError) as ex:
            generate_place(name=name)
        self.assertRegex(str(ex.exception), r'.*value too long.*')

    def test_name_none_ko(self):
        with self.assertRaises(IntegrityError) as ex:
            generate_place(name=None)
        self.assertRegex(str(ex.exception), r'.*(null|NULL).*(constraint|CONSTRAINT).*')

    def test_resolve_icon(self):
        for site_type in self.model.ICON_RESOLVERS.keys():
            obj = generate_place(name=fake.country(), site_type=site_type)
            expected_url = '<i class="{}"></i>'.format(self.model.ICON_RESOLVERS.get(site_type, ''))
            self.assertEqual(expected_url, obj.resolve_icon())


class TestRace(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = Race
        cls.m2m_model = RaceUser

    def test_create_ok(self):
        instance = self.model.objects.create(name=fake.word(), description=fake.paragraph())
        self.model.objects.get(pk=instance.pk)

    def test_create_with_owner_ok(self):
        instance = self.model.objects.create(name=fake.word(), description=fake.paragraph())
        users = baker.make(constants.REGISTRATION_USER, 3)
        instance.add_owners(*users)

        owners = instance.owners
        result = all(user in owners for user in users)
        self.assertTrue(result)

    def test_str_ok(self):
        instance = self.model.objects.create(name=fake.word(), description=fake.paragraph())
        expected = f'{instance.name} [{instance.pk}]'

        self.assertEqual(expected, str(instance))


class TestRaceUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = RaceUser

    def setUp(self):
        self.user = baker.make(constants.REGISTRATION_USER)
        self.race = baker.make(constants.ROLEPLAY_RACE)

    def test_str_ok(self):
        instance = self.model.objects.create(user=self.user, race=self.race)
        expected = f'{instance.user.username} <-> {instance.race.name}'

        self.assertEqual(expected, str(instance))


class TestCampaign(TestCase):
    model = Campaign

    @classmethod
    def setUpTestData(cls):
        # NOTE: This is done because it's better performance than creating a new entries each time
        cls.chat = baker.make_recipe('chat.chat')
        cls.world = generate_place(site_type=SiteTypes.WORLD)
        cls.owner = baker.make_recipe('registration.user')

    def setUp(self):
        self.name = fake.sentence(nb_words=3)
        self.instance = self.model.objects.create(
            name=self.name, chat=self.chat, system=random.choice(RoleplaySystems.values), place=self.world,
            owner=self.owner,
        )

    def test_str_ok(self):
        expected = f'{self.name} [{self.instance.pk}]'

        self.assertEqual(expected, str(self.instance))

    def test_add_game_masters(self):
        game_masters = baker.make(constants.REGISTRATION_USER, 3)
        self.instance.add_game_masters(*game_masters)

        self.assertEqual(len(self.instance.game_masters), len(game_masters))

    def test_discord_channel_empty_is_none(self):
        self.assertIsNone(self.instance.discord_channel)

    @unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_discord_channel_ok(self):
        self.instance.discord_channel_id = CHANNEL
        self.instance.save()
        self.assertIsNotNone(self.instance.discord_channel)

    def test_vote_ok(self):
        self.instance.vote(self.owner, True)
        instance = self.model.objects.with_votes().get(pk=self.instance.pk)

        self.assertEqual(instance.positive_votes, 1)

    def test_clean_start_date_greater_end_date_ko(self):
        self.instance.start_date = timezone.now() + timedelta(days=1)
        self.instance.end_date = timezone.now()

        with self.assertRaises(ValidationError) as ex:
            self.instance.clean()
        ex = ex.exception
        self.assertEqual('Start date must be before end date.', ex.message)


class TestPlayerInCampaign(TestCase):
    model = PlayerInCampaign

    @classmethod
    def setUpTestData(cls):
        cls.campaign = baker.make(constants.ROLEPLAY_CAMPAIGN)
        cls.user = baker.make(constants.REGISTRATION_USER)

    def test_str_ok(self):
        instance = self.model.objects.create(campaign=self.campaign, user=self.user)
        expected = f'{instance.user.username} in campaign {instance.campaign.name} (Game Master: False)'

        self.assertEqual(expected, str(instance))


class TestSession(TestCase):
    model = Session

    @classmethod
    def setUpTestData(cls):
        cls.campaign = baker.make_recipe('roleplay.campaign')

    def test_str_ok(self):
        name = fake.word()
        instance = self.model.objects.create(
            name=name,
            campaign=self.campaign,
        )
        expected = f'{name} [{instance.campaign.get_system_display()}]'

        self.assertEqual(expected, str(instance))
