#! /usr/bin/env python3

import pytest

PYTEST_ARGS = {
    'default': [],
    'fast': ['-q']
}

if __name__ == '__main__':
    pytest.main(['tests'])
