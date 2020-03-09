# pylint: disable=no-member
# La línea superior le dice a pylint que ignore los métodos generados en caliente por faker
import pytz

from django.contrib.auth.models import User
from faker import Factory

from factory import ModelFactory
from .models import Profile, ProfileImage

# Puedes encontrar una lista de providers en https://faker.readthedocs.io/en/master/providers.html
faker = Factory.create('es_ES')


class UserFactory(ModelFactory):
    """
    Esta clase generará en masa registros falsos para el modelo :class:User.
    """

    model = User  # Modelo a atacar

    def __init__(self):
        # Atributos del modelo
        self.username = faker.user_name()
        self.email = faker.email()
        self.password = faker.word()
        self.first_name = faker.first_name() if faker.boolean(chance_of_getting_true=50) else ''
        self.last_name = faker.last_name() if faker.boolean(chance_of_getting_true=50) else ''


class ProfileFactory(ModelFactory):
    """
    Esta clase generará en masa registros para el modelo :class:Profile.
    """

    model = Profile  # Modelo a atacar

    def __init__(self):
        # Atributos del modelo
        self.user = UserFactory.make()
        self.bio = faker.text()
        self.birthday = faker.date()


class ProfileImageFactory(ModelFactory):
    """
    Esta clase generará en masa registros para el modelo :class:ProfileImage.
    """

    model = ProfileImage  # Modelo a atacar

    def __init__(self):
        # Atributos del modelo
        self.profile = ProfileFactory.make()
        self.image = faker.file_name(category='Image', extension='jpg')
