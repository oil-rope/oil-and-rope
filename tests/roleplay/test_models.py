import unittest

from django.db import connection
from django.db.utils import DataError, IntegrityError
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from roleplay import models


class TestDomain(TestCase):
    connection_engine = connection.features.connection.settings_dict.get('ENGINE', None)

    def setUp(self):
        self.faker = Faker()
        self.model = models.Domain

    def test_str_ok(self):
        domain = baker.make(self.model)
        self.assertEqual(str(domain), domain.name)

    def test_ok(self):
        entries = self.faker.random_int(max=100)
        baker.make(self.model, entries)
        self.assertEqual(entries, self.model.objects.count())

    @unittest.skipIf('sqlite3' in connection_engine, 'SQLite takes Varchar as Text')
    def test_max_name_length_ko(self):
        name = 'This is a really long name that does not fit in characters'
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
