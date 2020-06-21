from asgiref.sync import sync_to_async
import functools


def async_get(model, **kwargs):
    """
    Returns `models.object.get(**kwargs)` as an async func so it can be called by `await`.
    """

    func = functools.partial(model.objects.get, **kwargs)
    async_func = sync_to_async(func)
    return async_func()


def async_add(manager, instance):
    """
    Returns `object.related_name.add(instance)` as an async func so it can be called by `await`.
    """

    func = functools.partial(manager.add, instance)
    async_func = sync_to_async(func)
    return async_func()


def async_get_or_create(model, **kwargs):
    """
    Returns `model.objects.get_or_create(**kwargs)` as an async func so it can called by `await`.
    """

    func = functools.partial(model.objects.get_or_create, **kwargs)
    async_func = sync_to_async(func)
    return async_func()
