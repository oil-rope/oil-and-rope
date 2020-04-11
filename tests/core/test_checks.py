import ast
import inspect

from django.db import models
from django.test import TestCase

from core.checks import get_argument


class DummyModel(models.Model):
    dummy_arg = models.CharField('Random')
    dummy_arg_2 = models.CharField(verbose_name='Random')

    class Meta:
        app_label = 'test_checks'


class TestCheck(TestCase):

    def setUp(self):
        self.dummy_model = DummyModel
        self.dummy_source = inspect.getsource(self.dummy_model)
        self.dummy_node_without_verbose_name = ast.parse(self.dummy_source).body[0].body[0]
        self.dummy_node_with_verbose_name = ast.parse(self.dummy_source).body[0].body[1]

    def test_model_with_verbose_name_ok(self):
        result = get_argument(self.dummy_node_with_verbose_name, 'verbose_name')
        self.assertIsNotNone(result)

    def test_model_withouth_verbose_name_ko(self):
        result = get_argument(self.dummy_node_without_verbose_name, 'verbose_name')
        self.assertIsNone(result)
