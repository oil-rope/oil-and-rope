from django.apps import apps

from common.constants import models


class DynamicMenuMiddleware:
    """
    Adds a cookie to track user when navigating our website, so we can
    know which part of the web did he/she came from.
    """

    def __init__(self, get_response):
        self.model = apps.get_model(models.DYNAMIC_MENU)
        self.get_response = get_response

    def __call__(self,  request):
        response = self.get_response(request)
        if '_auth_user_menu_referrer' not in request.COOKIES:
            response.set_cookie('_auth_user_menu_referrer', None)
            return response

        try:
            import ipdb; ipdb.set_trace()
            self.model.objects.get(pk=request.COOKIES['_auth_user_menu_referrer'])
        except self.model.DoesNotExist:
            response.set_cookie('_auth_user_menu_referrer', None)
        finally:
            return response
