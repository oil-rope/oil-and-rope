from rest_framework.routers import DefaultRouter

from ..viewsets.dynamic_menu import DynamicMenuViewSet

router = DefaultRouter()
router.register(prefix=r'menu', viewset=DynamicMenuViewSet, basename='menu')

urls = router.urls
