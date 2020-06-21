import functools

from asgiref.sync import sync_to_async


def async_manager_func(model, func, **kwargs):
    """
    Returns a function from `model.objects.func` as an async func so it can be called by `await`.
    """

    if not hasattr(model.objects, func):
        raise ImportError(f'{func} is not a manager function.')

    func = getattr(model.objects, func)
    func = functools.partial(func, **kwargs)
    async_func = sync_to_async(func)
    return async_func()


def async_get(model, **kwargs):
    """
    Returns `models.object.get(**kwargs)` as an async func so it can be called by `await`.
    """

    return async_manager_func(model, 'get', **kwargs)


def async_get_or_create(model, **kwargs):
    """
    Returns `model.objects.get_or_create(**kwargs)` as an async func so it can be called by `await`.
    """

    return async_manager_func(model, 'get_or_create', **kwargs)


def async_filter(model, **kwargs):
    """
    Returns `model.objects.filter(**kwargs)` as an async func so it can be called by `await`.
    """

    return async_manager_func(model, 'filter', **kwargs)


def async_add(manager, instance):
    """
    Returns `object.related_name.add(instance)` as an async func so it can be called by `await`.
    """

    func = functools.partial(manager.add, instance)
    async_func = sync_to_async(func)
    return async_func()
