"""oilandrope URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    # Prometheus metrics
    path('', include('django_prometheus.urls')),
    # API is served by Django REST Framework
    path('api/', include('api.urls')),
    # JavaScript translations
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

custom_admin_site = admin.site
custom_admin_site.site_title = _('Oil & Rope Admin Site')
custom_admin_site.site_header = _('Oil & Rope Admin Site')

urlpatterns += i18n_patterns(
    # Main site
    path('', include('core.urls')),
    # Admin site
    path('admin/', custom_admin_site.urls),
    # Common
    path('common/', include('common.urls')),
    # Auth system
    path('accounts/', include('registration.urls')),
    # oAuth
    path('oauth/', include('allauth.urls')),
    # Bot
    path('bot/', include('bot.urls')),
    # Roleplay
    path('roleplay/', include('roleplay.urls')),
    # O&R Email
    path('email/', include('oar_email.urls')),
    prefix_default_language=True,
)

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))
