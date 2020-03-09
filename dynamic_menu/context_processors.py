import logging

from django.contrib.auth.models import Permission
from django.db.models import Q, QuerySet

from . import models


def menus(request) -> dict:
    """
    Checks for menus, their permissions and return a queryset filtered.
    """

    # Checking for user and its permissions
    user = request.user
    user_permissions = [per.split('.')[1]
                        for per in user.get_all_permissions()]
    user_permissions = Permission.objects.filter(codename__in=user_permissions)

    # Getting menus
    qs = models.DynamicMenu.objects.all()

    # Filtering by permissions
    qs = qs.filter(
        Q(permissions_required__in=user_permissions) | Q(
            permissions_required__isnull=True),
    )
    qs = qs.filter(menu_type=models.DynamicMenu.MAIN_MENU)
    qs = qs.distinct()

    # Getting referrer
    menu_referrer = request.COOKIES.get('_auth_user_menu_referrer', None)
    if menu_referrer and menu_referrer != 'None':  # Because of JavaScript
        try:
            menu_parent = models.DynamicMenu.objects.get(pk=menu_referrer)
            context_menus = menu_parent.get_descendants()

            # Checking for permissions
            context_menus = context_menus.filter(
                Q(permissions_required__in=user_permissions) | Q(
                    permissions_required__isnull=True),
            )
            context_menus = context_menus.distinct()
        except models.DynamicMenu.DoesNotExist as ex:
            request.COOKIES['_auth_user_menu_referrer'] = None
            context_menus = QuerySet(model=models.DynamicMenu)
            logging.warning('Trying to access an non-existent menu.\n%s', ex)
    else:
        context_menus = QuerySet(model=models.DynamicMenu)

    return {
        'menus': qs,
        'context_menus': context_menus
    }
