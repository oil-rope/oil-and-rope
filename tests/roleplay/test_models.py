import os
import pathlib
import tempfile
import unittest
from datetime import datetime

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.utils import DataError, IntegrityError
from django.shortcuts import resolve_url
from django.test import TestCase
from freezegun import freeze_time
from model_bakery import baker

from common.constants import models as constants
from roleplay.enums import DomainTypes, RoleplaySystems, SiteTypes
from tests import fake

Domain = apps.get_model(constants.DOMAIN_MODEL)
Place = apps.get_model(constants.PLACE_MODEL)
PlayerInSession = apps.get_model(constants.ROLEPLAY_PLAYER_IN_SESSION)
Race = apps.get_model(constants.RACE_MODEL)
RaceUser = apps.get_model(constants.USER_RACE_RELATION)
Session = apps.get_model(constants.SESSION_MODEL)
User = apps.get_model(constants.USER_MODEL)

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
    @classmethod
    def setUpTestData(cls):
        cls.model = Place
        cls.enum = SiteTypes

    def test_str_ok(self):
        place = baker.make(self.model)
        self.assertEqual(str(place), place.name)

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
            place = self.model.objects.create(name=fake.country(), parent_site=parent)
            place.image = image
            place.save()
            parent = place

        obj_images = self.model.objects.first().images
        self.assertEqual(len(images), len(obj_images))

        for place in self.model.objects.all():
            os.unlink(place.image.path)

    # TODO: Refactor this test so is not that complex
    def test_nested_world_ok(self):  # noqa
        universe = self.model.objects.create(name='Universe', site_type=self.enum.WORLD)
        world = self.model.objects.create(name='World', site_type=self.enum.WORLD, parent_site=universe)

        self.assertIn(world, universe.get_worlds())

        continents = []
        for _ in range(0, 3):
            continents.append(
                self.model.objects.create(name=fake.country(), site_type=self.enum.CONTINENT, parent_site=world)
            )

        countries = []
        seas = []
        rivers = []
        unusual = []
        for continent in continents:
            self.assertIn(continent, world.get_continents())
            countries.append(
                self.model.objects.create(
                    name=fake.country(), site_type=self.enum.COUNTRY, parent_site=continent
                )
            )
            seas.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.SEA, parent_site=continent)
            )
            rivers.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.RIVER, parent_site=continent)
            )
            unusual.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.UNUSUAL, parent_site=continent)
            )

        for sea in seas:
            self.assertIn(sea, world.get_seas())

        for river in rivers:
            self.assertIn(river, world.get_rivers())

        for unusual in unusual:
            self.assertIn(unusual, world.get_unusual())

        islands = []
        cities = []
        mountains = []
        mines = []
        deserts = []
        tundras = []
        hills = []
        metropolis = []
        for country in countries:
            self.assertIn(country, world.get_countries())
            islands.append(
                self.model.objects.create(name=fake.country(), site_type=self.enum.ISLAND, parent_site=country)
            )
            cities.append(
                self.model.objects.create(name=fake.city(), site_type=self.enum.CITY, parent_site=country)
            )
            mountains.append(
                self.model.objects.create(
                    name=fake.country(), site_type=self.enum.MOUNTAINS, parent_site=country
                )
            )
            deserts.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.DESERT, parent_site=country)
            )
            hills.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.HILLS, parent_site=country)
            )
            tundras.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.TUNDRA, parent_site=country)
            )
            mines.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.MINES, parent_site=country)
            )
            metropolis.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.METROPOLIS, parent_site=country)
            )

        forests = []
        for island in islands:
            self.assertIn(island, world.get_islands())
            forests.append(
                self.model.objects.create(name=fake.name(), site_type=self.enum.FOREST, parent_site=island)
            )

        for m in metropolis:
            self.assertIn(m, world.get_metropolis())

        villages = []
        towns = []
        for city in cities:
            self.assertIn(city, world.get_cities())
            villages.append(
                self.model.objects.create(name=fake.city(), site_type=self.enum.VILLAGE, parent_site=city)
            )
            towns.append(
                self.model.objects.create(name=fake.city(), site_type=self.enum.TOWN, parent_site=city)
            )

        houses = []
        for village in villages:
            self.assertIn(village, world.get_villages())
            houses.append(
                self.model.objects.create(name=fake.city(), site_type=self.enum.HOUSE, parent_site=village)
            )

        for town in towns:
            self.assertIn(town, world.get_towns())

        for house in houses:
            self.assertIn(house, world.get_houses())

        for mountain in mountains:
            self.assertIn(mountain, world.get_mountains())

        for mine in mines:
            self.assertIn(mine, world.get_mines())

        for desert in deserts:
            self.assertIn(desert, world.get_deserts())

        for hill in hills:
            self.assertIn(hill, world.get_hills())

        for forest in forests:
            self.assertIn(forest, world.get_forests())

        for tundra in tundras:
            self.assertIn(tundra, world.get_tundras())

    @unittest.skipIf('sqlite3' in connection_engine, 'SQLite takes Varchar as Text')
    def test_max_name_length_ko(self):
        name = fake.password(length=101)
        with self.assertRaises(DataError) as ex:
            self.model.objects.create(name=name)
        self.assertRegex(str(ex.exception), r'.*value too long.*')

    def test_name_none_ko(self):
        with self.assertRaises(IntegrityError) as ex:
            self.model.objects.create(name=None)
        self.assertRegex(str(ex.exception), r'.*(null|NULL).*(constraint|CONSTRAINT).*')

    def test_is_house_ok(self):
        place = baker.make(self.model, site_type=self.enum.HOUSE)
        self.assertTrue(place.is_house)

    def test_is_town_ok(self):
        place = baker.make(self.model, site_type=self.enum.TOWN)
        self.assertTrue(place.is_town)

    def test_is_village_ok(self):
        place = baker.make(self.model, site_type=self.enum.VILLAGE)
        self.assertTrue(place.is_village)

    def test_is_city_ok(self):
        place = baker.make(self.model, site_type=self.enum.CITY)
        self.assertTrue(place.is_city)

    def test_is_metropolis_ok(self):
        place = baker.make(self.model, site_type=self.enum.METROPOLIS)
        self.assertTrue(place.is_metropolis)

    def test_is_forest_ok(self):
        place = baker.make(self.model, site_type=self.enum.FOREST)
        self.assertTrue(place.is_forest)

    def test_is_hills_ok(self):
        place = baker.make(self.model, site_type=self.enum.HILLS)
        self.assertTrue(place.is_hills)

    def test_is_mountains_ok(self):
        place = baker.make(self.model, site_type=self.enum.MOUNTAINS)
        self.assertTrue(place.is_mountains)

    def test_is_mines_ok(self):
        place = baker.make(self.model, site_type=self.enum.MINES)
        self.assertTrue(place.is_mines)

    def test_is_river_ok(self):
        place = baker.make(self.model, site_type=self.enum.RIVER)
        self.assertTrue(place.is_river)

    def test_is_sea_ok(self):
        place = baker.make(self.model, site_type=self.enum.SEA)
        self.assertTrue(place.is_sea)

    def test_is_desert_ok(self):
        place = baker.make(self.model, site_type=self.enum.DESERT)
        self.assertTrue(place.is_desert)

    def test_is_tundra_ok(self):
        place = baker.make(self.model, site_type=self.enum.TUNDRA)
        self.assertTrue(place.is_tundra)

    def test_is_unusual_ok(self):
        place = baker.make(self.model, site_type=self.enum.UNUSUAL)
        self.assertTrue(place.is_unusual)

    def test_is_island_ok(self):
        place = baker.make(self.model, site_type=self.enum.ISLAND)
        self.assertTrue(place.is_island)

    def test_is_country_ok(self):
        place = baker.make(self.model, site_type=self.enum.COUNTRY)
        self.assertTrue(place.is_country)

    def test_is_continent_ok(self):
        place = baker.make(self.model, site_type=self.enum.CONTINENT)
        self.assertTrue(place.is_continent)

    def test_is_world_ok(self):
        place = baker.make(self.model, site_type=self.enum.WORLD)
        self.assertTrue(place.is_world)

    def test_resolve_icon(self):
        for site_type in self.model.ICON_RESOLVERS.keys():
            obj = self.model.objects.create(name=fake.country(), site_type=site_type)
            expected_url = '<i class="{}"></i>'.format(self.model.ICON_RESOLVERS.get(site_type, ''))
            self.assertEqual(expected_url, obj.resolve_icon())

    def test_user_but_no_owner_save_ko(self):
        user = baker.make(User)
        with self.assertRaises(IntegrityError) as ex:
            self.model.objects.create(
                name=fake.city(),
                user=user
            )
        self.assertEqual(str(ex.exception), 'a private world must have owner.')

    def test_user_but_no_owner_clean_ko(self):
        user = baker.make(User)
        world = self.model.objects.create(
            name=fake.city(),
            user=user,
            owner=user
        )
        world.owner = None

        with self.assertRaises(ValidationError) as ex:
            world.clean()
        ex = ex.exception
        self.assertIn('user', ex.error_dict)
        message = ex.error_dict['user'][0].message
        self.assertEqual(message, 'a private world must have owner.')


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
        users = baker.make(constants.USER_MODEL, 3)
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
        self.user = baker.make(constants.USER_MODEL)
        self.race = baker.make(constants.RACE_MODEL)

    def test_str_ok(self):
        instance = self.model.objects.create(user=self.user, race=self.race)
        expected = f'{instance.user.username} <-> {instance.race.name}'

        self.assertEqual(expected, str(instance))


class TestSession(TestCase):
    model = Session

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.chat = baker.make_recipe('chat.chat')
        cls.world = baker.make_recipe('roleplay.world')

    def test_str_ok(self):
        name = fake.word()
        instance = self.model.objects.create(
            name=name,
            chat=self.chat,
            system=RoleplaySystems.PATHFINDER,
            world=self.world,
        )
        system = RoleplaySystems(instance.system)
        expected = f'{name} [{system.label.title()}]'

        self.assertEqual(expected, str(instance))

    def test_clean_non_world_ko(self):
        place = baker.make(constants.PLACE_MODEL, site_type=SiteTypes.CITY)
        session = self.model(
            name=fake.word(),
            plot=fake.paragraph(),
            next_game=datetime.now(),
            system=RoleplaySystems.PATHFINDER,
            world=place,
        )

        with self.assertRaisesRegex(ValidationError, 'World must be a world'):
            session.clean()

    def test_clean_no_world_given_ko(self):
        session = self.model(
            name=fake.word(),
            plot=fake.paragraph(),
            next_game=datetime.now(),
            system=RoleplaySystems.PATHFINDER,
        )

        with self.assertRaisesRegex(ValidationError, 'Session hasn\'t any world'):
            session.clean()

    def test_add_game_masters_ok(self):
        iterations = fake.pyint(min_value=1, max_value=10)
        users = baker.make(_model=User, _quantity=iterations)
        instace = baker.make(self.model, world=self.world)
        queries = (
            'Bulk Create',
        )

        with self.assertNumQueries(len(queries)):
            instace.add_game_masters(*users)

        expected = iterations
        result = PlayerInSession.objects.filter(
            player__in=users,
            is_game_master=True
        ).count()

        self.assertEqual(expected, result)

    def test_property_game_masters_ok(self):
        iterations = fake.pyint(min_value=1, max_value=10)
        users = baker.make(_model=User, _quantity=iterations)
        instace = baker.make(self.model, world=self.world)
        instace.add_game_masters(*users)

        expected = iterations
        result = instace.game_masters.count()

        self.assertEqual(expected, result)

    def test_get_absolute_url(self):
        instance = baker.make(self.model, world=self.world)
        expected_url = resolve_url(instance)
        url = instance.get_absolute_url()

        self.assertEqual(expected_url, url)


class TestPlayerInSession(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.model = PlayerInSession
        cls.world = baker.make(Place, site_type=SiteTypes.WORLD)
        cls.session = baker.make(Session, world=cls.world)

    def setUp(self):
        self.instance = baker.make(self.model, session=self.session)

    def test_str_ok(self):
        expected_str = '%(player)s in %(session)s (Game Master: %(is_game_master)s)' % {
            'player': self.instance.player,
            'session': self.instance.session,
            'is_game_master': self.instance.is_game_master,
        }
        result_str = str(self.instance)

        self.assertEqual(expected_str, result_str)
