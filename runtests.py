#! /usr/bin/env python3

import argparse
import subprocess
import sys
from io import StringIO

import django
import pytest
from django.core.management import call_command

parser = argparse.ArgumentParser(description='Run Tests and Linting.')

PYTEST_ARGS = {
    'default': ['tests'],
    'fast': ['tests', '-q']
}
COVERAGE_ARGS = ['--cov', './', '--cov-report', 'xml']

EXCLUDE_PATTERNS = ['**/migrations/**', 'heroku_settings.py']
FLAKE8_ARGS = ['--exclude'] + EXCLUDE_PATTERNS

ISORT_ARGS = ['--recursive', '--check-only', '--diff']


def exit_on_failure(ret, message=None):
    if ret:
        sys.exit(ret)


def flake8_main(args):
    print('Running flake8 code linting')
    ret = subprocess.call(['flake8'] + [str(arg) for arg in args])
    print('flake8 failed' if ret else 'flake8 passed')
    return ret


def isort_main(args):
    print('Running isort code checking')
    ret = subprocess.call(['isort'] + args)

    if ret:
        print('isort failed: Some modules have incorrectly ordered imports. Fix by running `isort --recursive .`')
    else:
        print('isort passed')

    return ret


def django_check(level='WARNING'):
    django.setup()
    out = StringIO()
    print('Checking Django')
    call_command('check', '--fail-leve=%s' % level, stdout=out)
    output = out.getvalue()

    if 'System check identified no issues' not in output:
        print('Django check failed.\n{}'.format(output))
        ret = 1
    else:
        print('Django check passed.')
        ret = 0

    return ret


parser.add_argument('--no-lint', action='store_true', help='Indicates to not run lintings.')
parser.add_argument('--lint-only', action='store_true', help='Runs only linting tests.')
parser.add_argument('--fast', action='store_true', help='Run pytest quiet.')
parser.add_argument('--coverage', action='store_true', help='Run coverage.')
parser.add_argument('--no-check', action='store_true', help='Indicates to not run django check.')


def run(_pytest, flake8, isort, _django):
    if _pytest:
        exit_on_failure(pytest.main(pytest_args))
    if flake8:
        exit_on_failure(flake8_main(FLAKE8_ARGS))
    if isort:
        exit_on_failure(isort_main(ISORT_ARGS))
    if _django:
        exit_on_failure(django_check())


if __name__ == '__main__':
    args = parser.parse_args()

    run_pytest = True
    run_flake8 = True
    run_isort = True
    run_django_check = True

    if args.lint_only:
        run_pytest = False
    if args.no_lint:
        run_flake8 = False
        run_isort = False
    if args.no_check:
        run_django_check = False
    if args.fast:
        pytest_args = PYTEST_ARGS['fast']
    else:
        pytest_args = PYTEST_ARGS['default']
    if args.coverage:
        pytest_args.extend(COVERAGE_ARGS)

    run(run_pytest, run_flake8, run_isort, run_django_check)
