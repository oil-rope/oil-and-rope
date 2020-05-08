from django.test import TestCase
from faker import Faker
from model_bakery import baker

from roleplay import models


class TestDomainManager(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.model = models.Domain
        self.number_of_domains = self.faker.pyint(min_value=0, max_value=100)
        self.number_of_subdomains = self.faker.pyint(min_value=0, max_value=100)
        baker.make(self.model, self.number_of_domains, domain_type=self.model.DOMAIN)
        baker.make(self.model, self.number_of_subdomains, domain_type=self.model.SUBDOMAIN)

    def test_all_ok(self):
        total = self.number_of_domains + self.number_of_subdomains
        self.assertEqual(total, self.model.objects.count())

    def test_domains_ok(self):
        self.assertEqual(self.number_of_domains, self.model.objects.domains().count())

    def test_subdomains_ok(self):
        self.assertEqual(self.number_of_subdomains, self.model.objects.subdomains().count())
