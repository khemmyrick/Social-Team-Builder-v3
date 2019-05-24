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
import django
import os

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import include, path

from . import views


def custom_page_not_found(request, term=None, pk=None):
    return django.views.defaults.page_not_found(request, None)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('404/', custom_page_not_found),
        path('', views.home, name='home'),
        path('admin/', admin.site.urls),
        path('markdownx/', include('markdownx.urls')),
        path('v3/accounts/', include('accounts.urls', namespace='accounts')),
        path('v3/accounts/', include('django.contrib.auth.urls')),
        # path('v3/accounts/', include('registration.backends.hmac.urls')),
        path('v3/projects/', include('projects.urls', namespace='projects')),
        path('__debug__/', include(debug_toolbar.urls)),
        path('<term>', custom_page_not_found),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += staticfiles_urlpatterns() # + urlpatterns
    # Commenting out '+ urlpatterns' seems to stop avatars from saving?
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


            # For django versions before 2.0:
            # url(r'^__debug__/', include(debug_toolbar.urls)),

    #    ] + urlpatterns