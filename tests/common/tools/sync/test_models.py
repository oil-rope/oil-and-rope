import pytest
from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from faker import Faker
from model_bakery import baker

from common.tools.sync import async_manager_func, async_get, async_get_or_create
from common.tools.sync.models import async_filter, async_add

User = apps.get_model(settings.AUTH_USER_MODEL)
Group = apps.get_model('auth.Group')

fake = Faker()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_manager_func_ok():
    await async_manager_func(User, 'all')


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_manager_func_ko():
    with pytest.raises(ImportError) as ex:
        await async_manager_func(User, 'non_existent_method')
    ex = ex.exconly()
    assert str(ex) == 'ImportError: non_existent_method is not a manager function.'


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_async_get_ok():
    user_created = baker.make(User)
    user_retrieved = await async_get(User, username=user_created.username)

    assert user_created == user_retrieved


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_async_get_or_create_ok():
    # Creates
    kwargs = {
        'username': fake.user_name(),
        'defaults': {
            'password': fake.password(),
            'email': fake.email()
        }
    }
    user_created, created = await async_get_or_create(User, **kwargs)
    assert created

    user_retrieved, created = await async_get_or_create(User, **kwargs)
    assert not created
    assert user_created == user_retrieved


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_async_filter():
    user = baker.make(User)
    users = await async_filter(User, username=user.username)
    count = sync_to_async(users.count)

    assert 1 == await count()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_async_add():
    user = baker.make(User)
    group = baker.make(Group)
    await async_add(user.groups, group)
    count = sync_to_async(user.groups.count)

    assert 1 == await count()
