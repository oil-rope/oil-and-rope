"""
Oil & Rope API
##############################################################################

Oil & Rope API System is a complex group of functions and views powered by DjangoRestFramework that allows the user to
access information through API calls.
"""

__title__ = 'Oil & Rope API System'
__version__ = (1, 0, 0)


def get_version() -> str:
    """
    Reads `__version__` from the top-level package.
    """

    return '.'.join(str(x) for x in __version__)
