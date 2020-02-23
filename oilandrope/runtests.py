#! /usr/bin/env python3

import os
import pytest

PYTEST_ARGS = {
    'default': ['tests'],
    'fast': ['-q']
}

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oilandrope.local_settings')

if __name__ == '__main__':
    pytest.main(args=PYTEST_ARGS['default'])
