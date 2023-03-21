#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

from common.utils.env import load_env_file, load_secrets


def main():
    BASE_DIR = Path(__file__).resolve().parent
    ENV_FILE = BASE_DIR / '.env'
    load_env_file(ENV_FILE)
    load_secrets()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oilandrope.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
