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
from django.views.i18n import JavaScriptCatalog

import bot.routing
import chat.routing

urlpatterns = [
    path('', include((bot.routing.websocket_urlpatterns, 'bot_ws'))),
    path('', include((chat.routing.websocket_urlpatterns, 'chat_ws'))),
]

urlpatterns += i18n_patterns(
    # JavaScript translations
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    # Main site
    path('', include('core.urls')),
    # Admin site
    path('admin/', admin.site.urls),
    # API
    path('api/', include('api.urls')),
    # Common
    path('common/', include('common.urls')),
    # Auth system
    path('accounts/', include('registration.urls')),
    # Bot
    path('bot/', include('bot.urls')),
    # Chat
    path('chat/', include('chat.urls')),
    # Dynamic Menu
    path('dynamic_menu/', include('dynamic_menu.urls')),
    # React FrontEnd
    path('frontend/', include('frontend.urls')),
    # Roleplay
    path('roleplay/', include('roleplay.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:  # pragma: no cover
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
