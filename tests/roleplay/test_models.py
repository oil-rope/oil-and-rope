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


class TestHomeland(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.model = models.Homeland

    def test_str_ok(self):
        homeland = baker.make(self.model)
        self.assertEqual(str(homeland), homeland.name)

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

        homeland = baker.make(self.model)
        homeland.image = image
        homeland.save()
        expected_path = '/media/roleplay/homeland/2020/01/01/{}/{}'.format(homeland.pk, image.name)
        expected_path = pathlib.Path(expected_path)
        self.assertIn(str(expected_path), homeland.image.path)

        tmpfile.close()
        os.unlink(tmpfile.name)
        os.unlink(homeland.image.path)

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
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertTrue(homeland.is_house)

    def test_is_town_ok(self):
        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertTrue(homeland.is_town)

    def test_is_village_ok(self):
        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertTrue(homeland.is_village)

    def test_is_city_ok(self):
        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertTrue(homeland.is_city)

    def test_is_metropolis_ok(self):
        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertTrue(homeland.is_metropolis)

    def test_is_forest_ok(self):
        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertTrue(homeland.is_forest)

    def test_is_hills_ok(self):
        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertTrue(homeland.is_hills)

    def test_is_mountains_ok(self):
        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertTrue(homeland.is_mountains)

    def test_is_mines_ok(self):
        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertTrue(homeland.is_mines)

    def test_is_river_ok(self):
        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertTrue(homeland.is_river)

    def test_is_sea_ok(self):
        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertTrue(homeland.is_sea)

    def test_is_desert_ok(self):
        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertTrue(homeland.is_desert)

    def test_is_tundra_ok(self):
        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertTrue(homeland.is_tundra)

    def test_is_unusual_ok(self):
        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertTrue(homeland.is_unusual)

    def test_is_house_ko(self):
        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_house)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_house)

    def test_is_town_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_town)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_town)

    def test_is_city_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_city)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_city)

    def test_is_village_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_village)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_village)

    def test_is_metropolis_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_metropolis)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_metropolis)

    def test_is_forest_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_forest)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_forest)

    def test_is_hills_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_hills)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_hills)

    def test_is_mountains_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_mountains)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_mountains)

    def test_is_mines_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_mines)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_mines)

    def test_is_river_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_river)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_river)

    def test_is_sea_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_sea)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_sea)

    def test_is_desert_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_desert)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_desert)

    def test_is_tundra_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_tundra)

        homeland = baker.make(self.model, site_type=self.model.UNUSUAL)
        self.assertFalse(homeland.is_tundra)

    def test_is_unusual_ko(self):
        homeland = baker.make(self.model, site_type=self.model.HOUSE)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.TOWN)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.CITY)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.METROPOLIS)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.FOREST)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.HILLS)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.MOUNTAINS)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.MINES)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.RIVER)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.SEA)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.DESERT)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.TUNDRA)
        self.assertFalse(homeland.is_unusual)

        homeland = baker.make(self.model, site_type=self.model.VILLAGE)
        self.assertFalse(homeland.is_unusual)
