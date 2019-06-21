from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path("login/", views.LogInView.as_view(), name="login"),
    path("logout/", views.LogOutView.as_view(), name="logout"),
    path('<pk>/', views.user_detail_view, name='details'),
    path('<pk>/edit/', views.user_update_view, name='edit'),
    path('<pk>/applications/', views.applications_view, name='applications'),
    path('<pk>/applications/bystatus/<term>',
         views.applications_view_bystatus,
         name='applicationsstatus'),
    path('<pk>/applications/byproject/<term>',
         views.applications_view_byproject,
         name='applicationsproject'),
    path('<pk>/applications/byposition/<term>',
         views.applications_view_byposition,
         name='applicationsposition'),
    path('<pk>/deactivate', views.user_deactivate_view, name='deactivate'),
    path('<pk>/deactivateconfirm',
         views.user_deactivate_confirm_view,
         name='deactivateconfirm'),
]
