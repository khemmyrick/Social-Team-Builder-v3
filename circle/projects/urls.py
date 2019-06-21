from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('new/', views.project_create_view, name='new'),
    path('search/', views.position_list_view, name='search'),
    path('search/showall/<showall>',
         views.position_list_view,
         name='searchall'),
    path('search/<term>', views.position_name_view, name='searchname'),
    path('<pk>/', views.project_detail_view, name='details'),
    path('<pk>/newposition/', views.position_create_view, name='newposition'),
    path('<pk>/position/<pospk>',
         views.position_detail_view,
         name='positiondetails'),
    path('<pk>/position/<pospk>/edit',
         views.position_update_view,
         name='changeposition'),
    path('<pk>/update', views.project_update_view, name='update'),
    path('<pk>/suspend', views.project_suspend_view, name='suspend'),
    path('<pk>/suspendconfirm',
         views.project_suspend_confirm_view,
         name='suspendconfirm'),
    # if a project is deactivated
    # project detail view sends creator to confirm_activate template
    path('<pk>/confirmactivate',
         views.project_confirm_activate_view,
         name='confirmactivate'),
    path('<pk>/apply', views.application_create_view, name='apply'),
    path('applicant/<pk>/hire', views.application_accept_view, name='hire'),
    path('applicant/<pk>/deny', views.application_deny_view, name='deny'),
]
