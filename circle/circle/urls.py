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

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from django_registration.backends.activation.views import (RegistrationView,
                                                           ActivationView)

from accounts.forms import UserRegistrationForm
from . import views


def custom_page_not_found(request, term=None, pk=None):
    return django.views.defaults.page_not_found(request, None)


urlpatterns = [
    path('404/', custom_page_not_found),
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
    path('v3/accounts/', include('accounts.urls', namespace='accounts')),
    path('v3/reg/activate/complete/',
         TemplateView.as_view(
            template_name='django_registration/activation_complete.html'
         ),
         name='django_registration_activation_complete'),
    path('v3/reg/activate/<str:activation_key>',
         ActivationView.as_view(),
         name='registration_activate'),
    path(
         'v3/reg/register/',
         RegistrationView.as_view(
            form_class=UserRegistrationForm
         ),
         name='django_registration_register',
    ),
    path('v3/reg/complete/',
         TemplateView.as_view(
            template_name='django_registration/registration_complete.html'
         ),
         name='django_registration_complete'),
    path('v3/reg/closed/',
         TemplateView.as_view(
            template_name='django_registration/registration_closed.html'
         ),
         name='django_registration_disallowed'),
    path('v3/reg/',
         include('django_registration.backends.activation.urls')
         ),
    path('v3/reg/', include('django.contrib.auth.urls')),
    path('v3/projects/', include('projects.urls', namespace='projects')),

    path('<term>', custom_page_not_found),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

    # urlpatterns += static(settings.STATIC_URL,
    # document_root=settings.STATIC_ROOT)

    # For django versions before 2.0:
    # url(r'^__debug__/', include(debug_toolbar.urls)),

    #    ] + urlpatterns
