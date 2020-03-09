class DynamicMenuMiddleware:
    """
    Adds a cookie to track user when navigating our website, so we can
    know which part of the web did he/she came from.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self,  request):
        response = self.get_response(request)
        if '_auth_user_menu_referrer' not in request.COOKIES:
            response.set_cookie('_auth_user_menu_referrer', None)
        return response
