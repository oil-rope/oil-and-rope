from . import models


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
                superuser_required=False,
                permissions_required__isnull=True,
            )
        }
        return menus_dict

    profile = user.profile
    menus = profile.menus
    menus_dict['menus'] = menus

    # Getting referrer
    menu_referrer = request.COOKIES.get('_auth_user_menu_referrer', None)
    if not menu_referrer or menu_referrer == 'None':  # Because of JavaScript
        return menus_dict

    return menus_dict
