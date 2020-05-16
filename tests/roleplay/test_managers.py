import functools

from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from roleplay import models


class TestDomainManager(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.model = models.Domain

        self.number_of_domains = self.faker.pyint(min_value=1, max_value=100)
        baker.make(self.model, self.number_of_domains, domain_type=self.model.DOMAIN)
        self.number_of_subdomains = self.faker.pyint(min_value=1, max_value=100)
        baker.make(self.model, self.number_of_subdomains, domain_type=self.model.SUBDOMAIN)

    def test_all_ok(self):
        total = self.number_of_domains + self.number_of_subdomains
        self.assertEqual(total, self.model.objects.count())

    def test_domains_ok(self):
        self.assertEqual(self.number_of_domains, self.model.objects.domains().count())

    def test_subdomains_ok(self):
        self.assertEqual(self.number_of_subdomains, self.model.objects.subdomains().count())


class TestPlaceManager(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.model = models.Place
        self.user = baker.make(get_user_model())
        random_int = functools.partial(self.faker.pyint, min_value=1, max_value=100)

        self.number_of_houses = random_int()
        baker.make(self.model, self.number_of_houses, site_type=self.model.HOUSE)
        self.number_of_towns = random_int()
        baker.make(self.model, self.number_of_towns, site_type=self.model.TOWN)
        self.number_of_villages = random_int()
        baker.make(self.model, self.number_of_villages, site_type=self.model.VILLAGE)
        self.number_of_cities = random_int()
        baker.make(self.model, self.number_of_cities, site_type=self.model.CITY)
        self.number_of_metropolis = random_int()
        baker.make(self.model, self.number_of_metropolis, site_type=self.model.METROPOLIS)
        self.number_of_forests = random_int()
        baker.make(self.model, self.number_of_forests, site_type=self.model.FOREST)
        self.number_of_hills = random_int()
        baker.make(self.model, self.number_of_hills, site_type=self.model.HILLS)
        self.number_of_mountains = random_int()
        baker.make(self.model, self.number_of_mountains, site_type=self.model.MOUNTAINS)
        self.number_of_mines = random_int()
        baker.make(self.model, self.number_of_mines, site_type=self.model.MINES)
        self.number_of_rivers = random_int()
        baker.make(self.model, self.number_of_rivers, site_type=self.model.RIVER)
        self.number_of_seas = random_int()
        baker.make(self.model, self.number_of_seas, site_type=self.model.SEA)
        self.number_of_deserts = random_int()
        baker.make(self.model, self.number_of_deserts, site_type=self.model.DESERT)
        self.number_of_tundras = random_int()
        baker.make(self.model, self.number_of_tundras, site_type=self.model.TUNDRA)
        self.number_of_unusuals = random_int()
        baker.make(self.model, self.number_of_unusuals, site_type=self.model.UNUSUAL)
        self.number_of_islands = random_int()
        baker.make(self.model, self.number_of_islands, site_type=self.model.ISLAND)
        self.number_of_countries = random_int()
        baker.make(self.model, self.number_of_countries, site_type=self.model.COUNTRY)
        self.number_of_continents = random_int()
        baker.make(self.model, self.number_of_continents, site_type=self.model.CONTINENT)
        self.number_of_worlds = random_int()
        baker.make(self.model, self.number_of_worlds, site_type=self.model.WORLD)

        self.total = self.number_of_houses + self.number_of_towns + self.number_of_villages + self.number_of_cities \
                     + self.number_of_metropolis + self.number_of_forests + self.number_of_hills \
                     + self.number_of_mountains + self.number_of_mines + self.number_of_rivers + self.number_of_seas \
                     + self.number_of_deserts + self.number_of_tundras + self.number_of_unusuals \
                     + self.number_of_islands + self.number_of_countries + self.number_of_continents \
                     + self.number_of_worlds

    def test_all_ok(self):
        self.assertEqual(self.total, self.model.objects.count())

    def test_user_places(self):
        quantity = 5
        expected_queries = 1
        baker.make(self.model, quantity, user=self.user)
        with self.assertNumQueries(expected_queries):
            result = self.model.objects.user_places(user=self.user)
            self.assertEqual(quantity, result.count())

    def test_community_places(self):
        expected_queries = 1
        with self.assertNumQueries(expected_queries):
            result = self.model.objects.community_places()
            self.assertEqual(self.total, result.count())

    def test_houses_ok(self):
        self.assertEqual(self.number_of_houses, self.model.objects.houses().count())

    def test_towns_ok(self):
        self.assertEqual(self.number_of_towns, self.model.objects.towns().count())

    def test_villages_ok(self):
        self.assertEqual(self.number_of_villages, self.model.objects.villages().count())

    def test_cities_ok(self):
        self.assertEqual(self.number_of_cities, self.model.objects.cities().count())

    def test_metropolis_ok(self):
        self.assertEqual(self.number_of_metropolis, self.model.objects.metropolis().count())

    def test_forests_ok(self):
        self.assertEqual(self.number_of_forests, self.model.objects.forests().count())

    def test_hills_ok(self):
        self.assertEqual(self.number_of_hills, self.model.objects.hills().count())

    def test_mountains_ok(self):
        self.assertEqual(self.number_of_mountains, self.model.objects.mountains().count())

    def test_mines_ok(self):
        self.assertEqual(self.number_of_mines, self.model.objects.mines().count())

    def test_rivers_ok(self):
        self.assertEqual(self.number_of_rivers, self.model.objects.rivers().count())

    def test_seas_ok(self):
        self.assertEqual(self.number_of_seas, self.model.objects.seas().count())

    def test_deserts_ok(self):
        self.assertEqual(self.number_of_deserts, self.model.objects.deserts().count())

    def test_tundras_ok(self):
        self.assertEqual(self.number_of_tundras, self.model.objects.tundras().count())

    def test_unusuals_ok(self):
        self.assertEqual(self.number_of_unusuals, self.model.objects.unusuals().count())

    def test_islands_ok(self):
        self.assertEqual(self.number_of_islands, self.model.objects.islands().count())

    def test_countries_ok(self):
        self.assertEqual(self.number_of_countries, self.model.objects.countries().count())

    def test_continents_ok(self):
        self.assertEqual(self.number_of_continents, self.model.objects.continents().count())

    def test_worlds_ok(self):
        self.assertEqual(self.number_of_worlds, self.model.objects.worlds().count())
