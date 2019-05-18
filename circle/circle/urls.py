"""circle URL Configuration

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
import os

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import include, path

from . import views


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('', views.home, name='home'),
        path('admin/', admin.site.urls),
        path('v3/accounts/', include('accounts.urls', namespace='accounts')),
        path('v3/accounts/', include('django.contrib.auth.urls')),
        # path('v3/accounts/', include('registration.backends.hmac.urls')),
        path('v3/projects/', include('projects.urls', namespace='projects')),
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += staticfiles_urlpatterns() + urlpatterns
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




            # For django versions before 2.0:
            # url(r'^__debug__/', include(debug_toolbar.urls)),

    #    ] + urlpatterns