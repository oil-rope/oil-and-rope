#! /usr/bin/env python3

import argparse
import subprocess
import sys

import pytest

parser = argparse.ArgumentParser(description='Run Tests and Linting.')

PYTEST_ARGS = {
    'default': ['tests'],
    'fast': ['tests', '-q']
}
COVERAGE_ARGS = ['--cov', './', '--cov-report', 'xml']

EXCLUDE_PATTERNS = ['**/migrations/**']
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


parser.add_argument('--no-lint', action='store_true',
                    help='Indicates to no run lintings.')
parser.add_argument('--lint-only', action='store_true',
                    help='Runs only linting tests.')
parser.add_argument('--fast', action='store_true', help='Run pytest quiet.')
parser.add_argument('--coverage', action='store_true', help='Run coverage.')

if __name__ == '__main__':
    args = parser.parse_args()

    run_pytest = True
    run_flake8 = True
    run_isort = True

    if args.lint_only:
        run_pytest = False
    if args.no_lint:
        run_flake8 = False
        run_isort = False
    if args.fast:
        pytest_args = PYTEST_ARGS['fast']
    else:
        pytest_args = PYTEST_ARGS['default']
    if args.coverage:
        pytest_args.extend(COVERAGE_ARGS)

    if run_pytest:
        exit_on_failure(pytest.main(pytest_args))
    if run_flake8:
        exit_on_failure(flake8_main(FLAKE8_ARGS))
    if run_isort:
        exit_on_failure(isort_main(ISORT_ARGS))
