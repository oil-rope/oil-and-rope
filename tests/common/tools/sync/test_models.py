import pytest
from django.apps import apps
from django.conf import settings

from common.tools.sync import async_manager_func

User = apps.get_model(settings.AUTH_USER_MODEL)
Group = apps.get_model('auth.Group')


@pytest.mark.asyncio
async def test_async_manager_func_ok():
    await async_manager_func(User, 'all')


@pytest.mark.asyncio
async def test_async_manager_non_existent_func_ko():
    func = 'non_existent_method'
    error_msg = r'{} is not a function for {}'.format(func, User.objects)
    with pytest.raises(ImportError, match=error_msg):
        await async_manager_func(User, func)


@pytest.mark.asyncio
async def test_async_manager_non_existent_manager_ko():
    manager = 'non_existent_manager'
    error_msg = r'{} is not a manager for {}.'.format(manager, User.__module__)
    with pytest.raises(ImportError, match=error_msg):
        await async_manager_func(User, 'all', manager=manager)
