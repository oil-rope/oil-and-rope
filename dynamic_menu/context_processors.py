from . import models


def filter_menus(menus, user):
    """
    Filters menus queryset from user based on permissions, staff...
    """

    # Comparing permissions
    user_perms = user.get_all_permissions()
    exclude_menus = []
    for menu in menus:
        menu_permissions = menu.permissions
        # Removing if staff are not accomplished
        if menu.staff_required and not user.is_staff:
            exclude_menus.append(menu.pk)
            continue
        # If menu has no permissions there's no need to further check
        if not menu_permissions:
            continue
        # If user has no perms but menu has it's automatic excluding
        if not user_perms:
            exclude_menus.append(menu.pk)
            continue
        # User must have all permissions in order to access a menu
        user_has_all_needed_perms = all([perm in user_perms for perm in menu_permissions])
        if not user_has_all_needed_perms:
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

    menus_dict = {
        'menus': list(),
        'context_menus': list()
    }

    user = request.user

    if not user.is_authenticated:
        menus_dict = {
            'menus': models.DynamicMenu.objects.filter(
                staff_required=False,
                permissions_required__isnull=True,
            ),
            'context_menus': models.DynamicMenu.objects.filter(
                staff_required=False,
                permissions_required__isnull=True,
            )
        }
        return menus_dict

    profile = user.profile
    menus = profile.menus
    context_menus = profile.get_context_menus(request)
    menus_dict['menus'] = menus
    menus_dict['context_menus'] = context_menus

    return menus_dict
