from django.conf import settings
from faker import Faker


def create_faker(locales: list = []) -> Faker:
    """
    Creates a :class:`~faker.Faker` setting locales from django settings languages.
    """

    locales = locales or [lan[0] for lan in settings.LANGUAGES]
    fake = Faker(locales)
    return fake
