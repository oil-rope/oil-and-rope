import functools

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


class TestHomelandManager(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.model = models.Homeland
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

    def test_all_ok(self):
        total = self.number_of_houses + self.number_of_towns + self.number_of_villages + self.number_of_cities \
                + self.number_of_metropolis + self.number_of_forests + self.number_of_hills + self.number_of_mountains \
                + self.number_of_mines + self.number_of_rivers + self.number_of_seas + self.number_of_deserts \
                + self.number_of_tundras + self.number_of_unusuals
        self.assertEqual(total, self.model.objects.count())

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
