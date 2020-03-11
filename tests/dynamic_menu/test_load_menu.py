import json
import pathlib
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from dynamic_menu import models


@pytest.fixture()
def create_data():
    """
    Creates data an returns the list.
    """

    data = [
        {
            'name': 'TestName',
            'menu_type': models.DynamicMenu.MAIN_MENU,
        },
        {
            'name': 'TestName2',
            'menu_type': models.DynamicMenu.CONTEXT_MENU,
        }
    ]

    return data


def test_syntax():
    """
    Checks if :class:`CommandError` are raised when syntax incorrect.
    """

    out = StringIO()
    with pytest.raises(CommandError,
                       match='.*arguments are required: fixture.*'):
        call_command('load_menu', stdout=out)


@pytest.mark.django_db
def test_load_data(create_data: list):
    """
    Checks if data is loaded when function called.
    """

    json_data = json.dumps(create_data)
    json_file = pathlib.Path('./init_menu.json')
    json_file.write_text(json_data)

    call_command('load_menu', str(json_file))

    assert models.DynamicMenu.objects.count() == len(create_data),\
        'Menu entries weren\'t correctly created.'

    json_file.unlink()
