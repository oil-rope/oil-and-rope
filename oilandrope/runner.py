from django.core.management.base import CommandParser


class PytestTestRunner:
    """Runs pytest to discover and run tests."""

    verbosity: int
    failfast: bool
    keepdb: bool
    cov: bool
    cov_report: bool

    def __init__(self, verbosity=1, failfast=False, keepdb=False, cov=False, cov_report=False, **kwargs):
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb
        self.cov = cov
        self.cov_report = cov_report

    @classmethod
    def add_arguments(cls, parser: CommandParser):
        parser.add_argument(
            '--keepdb', action='store_true',
            help='Preserves the test DB between runs.'
        )
        parser.add_argument(
            '--cov',
            action='store_true',
            help='Declares if coverage needs to be run and collected.',
        )
        parser.add_argument(
            '--cov-report',
            action='store_true',
            help='Generates an output of the missing lines to be covered.',
        )

    def run_tests(self, test_labels):
        """
        Run pytest and return the exitcode.

        It translates some of Django's test command option to pytest's.
        """

        import pytest

        argv = []
        if self.verbosity == 0:
            argv.append('--quiet')
        if self.verbosity == 2:
            argv.append('--verbose')
        if self.verbosity == 3:
            argv.append('-vv')
        if self.failfast:
            argv.append('--exitfirst')
        if self.keepdb:
            argv.append('--reuse-db')

        argv.extend(test_labels)

        if not self.cov:
            return pytest.main(argv)
        else:
            import coverage.control

            # We create the Coverage tool and execute it by hand
            cov = coverage.control.Coverage()
            cov.start()

            test_exit_code = pytest.main(argv)

            cov.stop()
            cov.save()

            cov.xml_report()
            cov.html_report()

            if self.cov_report:
                cov.report(skip_covered=True)

            return test_exit_code
