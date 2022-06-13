from django.test import TestCase
from django_filters.filters import Filter

from common.filters.mixins import FilterCapitalizeMixin


class TestFilterCapitalizeMixin(TestCase):
    def setUp(self):
        class DummyFilterSet(FilterCapitalizeMixin):
            filters = {
                'test_filter': Filter(
                    label='test filter',
                    field_name='test_filter',
                    lookup_expr='exact',
                    help_text='test filter help text',
                )
            }
        self.filter_class = DummyFilterSet

    def test_filter_with_no_filters_attribute_ko(self):
        with self.assertRaises(AttributeError):
            self.filter_class.filters = None
            self.filter_class()

    def test_filter_capitalize_label_ok(self):
        filter_obj = self.filter_class()
        filter = filter_obj.filters['test_filter']
        self.assertEqual(filter.label, 'Test filter')

    def test_filter_capitalize_help_text_ok(self):
        filter_obj = self.filter_class()
        filter = filter_obj.filters['test_filter']
        self.assertEqual(filter.extra['help_text'], 'Test filter help text')
