from django.conf import settings
from faker import Faker


def create_faker() -> Faker:
    """
    Creates a :class:`Faker` setting locales from django settings languages.
    """

    fake = Faker([lan[0] for lan in settings.LANGUAGES])
    return fake
