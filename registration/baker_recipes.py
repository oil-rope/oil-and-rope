from django.apps import apps
from model_bakery.recipe import Recipe

from common.constants import models
from common.utils import create_faker

User = apps.get_model(models.USER_MODEL)

fake = create_faker()

user = Recipe(
    User,
    username=fake.user_name,
    email=fake.email,
    password=fake.password,
    first_name=fake.first_name,
    last_name=fake.last_name,
    is_premium=False,
    is_staff=False,
    is_active=True,
)

inactive_user = user.extend(
    is_active=False
)

staff_user = user.extend(
    is_staff=True
)

premium_user = user.extend(
    is_premium=True
)
