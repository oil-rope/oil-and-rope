import pytest
from django.test import Client
from model_bakery import baker

from dynamic_menu import models


@pytest.fixture()
def create_dynamic_menu():
    """
    Fakes instances to test.
    """

    return baker.make(models.DynamicMenu)


@pytest.mark.django_db
def test_str_is_correct(client: Client, create_dynamic_menu: models.DynamicMenu):
    """
    Checks if `__str__` works correctly with `mark_safe`.
    """

    prepended_text = '<i class="md md-prepended-icon"></i>'
    appended_text = '<i class="md md-appended-icon"></i>'

    create_dynamic_menu.prepended_text = prepended_text
    create_dynamic_menu.appended_text = appended_text
    create_dynamic_menu.save()

    assert prepended_text in str(create_dynamic_menu),\
        'Prepended text isn\'t marked as safe.'
    assert appended_text in str(create_dynamic_menu),\
        'Appended text isn\'t marked as safe.'

    assert create_dynamic_menu.url == '#no-url',\
        'URL Resolver works without resolver.'
