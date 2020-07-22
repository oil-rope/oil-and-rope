import logging

from . import models
from .enums import MenuTypes


def filter_menus(menus, user):
    """
    Filters menus queryset from user based on permissions, staff, superuser...
    """

    # Comparing permissions
    user_perms = user.get_all_permissions()
    exclude_menus = []
    for menu in menus:
        menu_permissions = menu.permissions
        # If menu has no permissions there's no need to further check
        if not menu_permissions:
            continue
        # If user has no perms but menu has it's automatic excluding
        if not user_perms:
            exclude_menus.append(menu.pk)
            continue
        # User must have all permissions in order to access a menu
        for perm in menu_permissions:
            if perm not in user_perms:
                exclude_menus.append(menu.pk)
                break
        # Removing if staff or superuser are not accomplished
        if menu.staff_required and not user.is_staff:
            exclude_menus.append(menu.pk)
            continue
        if menu.superuser_required and not user.is_superuser:
            exclude_menus.append(menu.pk)
            continue

    # Removing from query
    if exclude_menus:
        menus = menus.exclude(pk__in=exclude_menus)

    return menus


def menus(request) -> dict:
    """
    Checks for menus, their permissions and return a queryset filtered.
    """

    user = request.user

    if not user.is_authenticated:
        menus_dict = {
            'menus': models.DynamicMenu.objects.filter(
                staff_required=False,
                superuser_required=False,
                permissions_required__isnull=True,
            ),
            'context_menus': models.DynamicMenu.objects.filter(
                staff_required=False,
                superuser_required=False,
                permissions_required__isnull=True,
            )
        }
        return menus_dict

    # Initialize dicts
    menus_dict = {
        'menus': models.DynamicMenu.objects.none(),
        'context_menus': models.DynamicMenu.objects.none()
    }

    # Getting menus
    qs = models.DynamicMenu.objects.filter(menu_type=MenuTypes.MAIN_MENU)
    if not qs.exists():  # Empty query does not need to continue
        return menus_dict

    qs = filter_menus(qs, user)

    # Getting referrer
    menu_referrer = request.COOKIES.get('_auth_user_menu_referrer', None)
    if menu_referrer and menu_referrer != 'None':  # Because of JavaScript
        try:
            menu_parent = models.DynamicMenu.objects.get(pk=menu_referrer)
            context_menus = menu_parent.get_children().filter(
                menu_type=MenuTypes.CONTEXT_MENU
            )
            context_menus = filter_menus(context_menus, user)
        except models.DynamicMenu.DoesNotExist as ex:
            request.COOKIES['_auth_user_menu_referrer'] = None
            context_menus = models.DynamicMenu.objects.none()
            logging.warning('Trying to access an non-existent menu.\n%s', ex)
        except ValueError as ex:
            request.COOKIES['_auth_user_menu_referrer'] = None
            context_menus = models.DynamicMenu.objects.none()
            logging.warning('Trying to access an non-existent menu.\n%s', ex)
    else:
        context_menus = models.DynamicMenu.objects.none()

    menus_dict['menus'] = qs
    menus_dict['context_menus'] = context_menus

    return menus_dict
