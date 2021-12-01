from channels.db import database_sync_to_async


async def async_manager_func(model, func, *, manager='objects', **kwargs):
    """
    Returns a function from `model.objects.func` as an async func so it can be called by `await`.

    Parameters
    ----------
    model: :class:`models.Model`
        Django model.
    func: :class:`str`
        Function to execute
    manager: :class:`str`
        Manager to use.
    """

    if not hasattr(model, manager):
        raise ImportError(f'{manager} is not a manager for {model.__module__}.')

    manager = getattr(model, manager)
    if not hasattr(manager, func):
        raise ImportError(f'{func} is not a function for {manager}.')

    func = getattr(model.objects, func)

    async_func = database_sync_to_async(func)
    return await async_func(**kwargs)
