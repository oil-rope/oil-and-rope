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

urlpatterns = []

urlpatterns += i18n_patterns(
    # Main site
    path('', include('core.urls')),
    # Admin site
    path('admin/', admin.site.urls),
    # Auth system
    path('accounts/', include('registration.urls')),
    # Bot
    path('bot/', include('bot.urls')),
    # Chat
    path('chat/', include('chat.urls')),
    # React FrontEnd
    path('frontend/', include('frontend.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
