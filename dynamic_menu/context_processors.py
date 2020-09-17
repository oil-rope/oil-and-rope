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
    context_menus = profile.get_context_menus(request)
    menus_dict['menus'] = menus
    menus_dict['context_menus'] = context_menus

    return menus_dict
