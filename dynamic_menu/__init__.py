# -*- coding: utf-8 -*-

"""
Dynamic Menu
~~~~~~~~~~~~

Menus are controlled by this package and dynamically created with references
to themselves.

:copyright: (c) 2019 LeCuay (Oil & Rope Team)
:license: MIT, see LICENSE for more details.

"""

import logging

VERSION = (0, 0, 1)


def get_version(version: tuple) -> str:
    """
    Gets the version of the package based on a :class:`tuple` and returns a :class:`str`.
    This method is based on ``django-extensions`` get_version method.
    """

    if not isinstance(version[-1], int):
        str_version = '.'.join(list(map(str, version[:-1])))
        str_version += '_{}'.format(version[-1])
        return str_version

    str_version = '.'.join(list(map(str, version)))
    return str_version


__title__ = 'Dynamic Menu'
__author__ = 'LeCuay (Oil & Rope Team)'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 LeCuay (Oil & Rope Team)'
__version__ = get_version(VERSION)


logging.getLogger(__name__).addHandler(logging.NullHandler())
