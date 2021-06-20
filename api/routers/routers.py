from collections import OrderedDict

from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter


class OilAndRopeDefaultRouter(DefaultRouter):
    """
    This router allows any user to access APIRootView but everything besides that works exactly like DefaultRouter.
    """

    def get_api_root_view(self, api_urls=None):
        """
        Exact same behaviour as DefaultRouter but allowing any only on APIRootView.
        """

        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        return self.APIRootView.as_view(api_root_dict=api_root_dict, permission_classes=[AllowAny])
