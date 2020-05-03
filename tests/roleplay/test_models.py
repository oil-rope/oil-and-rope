import os
import pathlib
import tempfile
import unittest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.utils import DataError, IntegrityError
from django.test import TestCase
from faker import Faker
from freezegun import freeze_time
from model_bakery import baker

from roleplay import models

connection_engine = connection.features.connection.settings_dict.get('ENGINE', None)


class TestDomain(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.model = models.Domain

    def test_str_ok(self):
        domain = baker.make(self.model)
        self.assertEqual(str(domain), domain.name)

    def test_ok(self):
        entries = self.faker.pyint(min_value=1, max_value=100)
        baker.make(self.model, entries)
        self.assertEqual(entries, self.model.objects.count())

    @unittest.skipIf('sqlite3' in connection_engine, 'SQLite takes Varchar as Text')
    def test_max_name_length_ko(self):
        name = self.faker.password(length=26)
        with self.assertRaises(DataError) as ex:
            self.model.objects.create(name=name)
        self.assertRegex(str(ex.exception), r'.*value too long.*')

    def test_name_none_ko(self):
        with self.assertRaises(IntegrityError) as ex:
            self.model.objects.create(name=None)
        self.assertRegex(str(ex.exception), r'.*(null|NULL).*(constraint|CONSTRAINT).*')

    def test_is_domain_ok(self):
        instance = baker.make(self.model, domain_type=self.model.DOMAIN)
        self.assertTrue(instance.is_domain)

    def test_is_domain_ko(self):
        instance = baker.make(self.model, domain_type=self.model.SUBDOMAIN)
        self.assertFalse(instance.is_domain)

    def test_is_subdomain_ok(self):
        instance = baker.make(self.model, domain_type=self.model.SUBDOMAIN)
        self.assertTrue(instance.is_subdomain)

    def test_is_subdomain_ko(self):
        instance = baker.make(self.model, domain_type=self.model.DOMAIN)
        self.assertFalse(instance.is_subdomain)


class TestPlace(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.model = models.Place

    def test_str_ok(self):
        place = baker.make(self.model)
        self.assertEqual(str(place), place.name)

    def test_ok(self):
        entries = self.faker.pyint(min_value=1, max_value=100)
        baker.make(self.model, entries)
        self.assertEqual(entries, self.model.objects.count())

    @freeze_time('2020-01-01')
    def test_image_upload_ok(self):
        tmpfile = tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', dir='./tests/', delete=False)
        image_data = open(tmpfile.name, 'rb').read()
        image_file = tmpfile.name
        image = SimpleUploadedFile(name=image_file, content=image_data, content_type='image/jpeg')

        place = baker.make(self.model)
        place.image = image
        place.save()
        expected_path = '/media/roleplay/place/2020/01/01/{}/{}'.format(place.pk, image.name)
        expected_path = pathlib.Path(expected_path)
        self.assertIn(str(expected_path), place.image.path)

        tmpfile.close()
        os.unlink(tmpfile.name)
        os.unlink(place.image.path)

    @unittest.skipIf('sqlite3' in connection_engine, 'SQLite takes Varchar as Text')
    def test_max_name_length_ko(self):
        name = self.faker.password(length=51)
        with self.assertRaises(DataError) as ex:
            self.model.objects.create(name=name)
        self.assertRegex(str(ex.exception), r'.*value too long.*')

    def test_name_none_ko(self):
        with self.assertRaises(IntegrityError) as ex:
            self.model.objects.create(name=None)
        self.assertRegex(str(ex.exception), r'.*(null|NULL).*(constraint|CONSTRAINT).*')

    def test_is_house_ok(self):
        place = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertTrue(place.is_house)

    def test_is_town_ok(self):
        place = baker.make(self.model, site_type=self.model.TOWN)
        self.assertTrue(place.is_town)

    def test_is_village_ok(self):
        place = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertTrue(place.is_village)

    def test_is_city_ok(self):
        place = baker.make(self.model, site_type=self.model.CITY)
        self.assertTrue(place.is_city)

    def test_is_metropolis_ok(self):
        place = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertTrue(place.is_metropolis)

    def test_is_forest_ok(self):
        place = baker.make(self.model, site_type=self.model.FOREST)
        self.assertTrue(place.is_forest)

    def test_is_hills_ok(self):
        place = baker.make(self.model, site_type=self.model.HILLS)
        self.assertTrue(place.is_hills)

    def test_is_mountains_ok(self):
        place = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertTrue(place.is_mountains)

    def test_is_mines_ok(self):
        place = baker.make(self.model, site_type=self.model.MINES)
        self.assertTrue(place.is_mines)

    def test_is_river_ok(self):
        place = baker.make(self.model, site_type=self.model.RIVER)
        self.assertTrue(place.is_river)

    def test_is_sea_ok(self):
        place = baker.make(self.model, site_type=self.model.SEA)
        self.assertTrue(place.is_sea)

    def test_is_desert_ok(self):
        place = baker.make(self.model, site_type=self.model.DESERT)
        self.assertTrue(place.is_desert)

    def test_is_tundra_ok(self):
        place = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertTrue(place.is_tundra)

    def test_is_unusual_ok(self):
        place = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertTrue(place.is_unusual)

    def test_is_island_ok(self):
        place = baker.make(self.model, site_type=self.model.ISLAND)
        self.assertTrue(place.is_island)

    def test_is_country_ok(self):
        place = baker.make(self.model, site_type=self.model.COUNTRY)
        self.assertTrue(place.is_country)

    def test_is_continent_ok(self):
        place = baker.make(self.model, site_type=self.model.CONTINENT)
        self.assertTrue(place.is_continent)

    def test_is_world_ok(self):
        place = baker.make(self.model, site_type=self.model.WORLD)
        self.assertTrue(place.is_world)
