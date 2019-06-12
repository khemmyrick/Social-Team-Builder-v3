from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    # path('new/', views.ProjectCreateView.as_view(), name='new'),
    path('new/', views.project_create_view, name='new'),
    # path('search/', views.ProjectListView.as_view(), name='search'),
    path('search/', views.position_list_view, name='search'),
    path('search/<term>', views.position_name_view, name='searchname'),
    # path('<pk>/', views.ProjectDetailView.as_view(), name='details'),
    path('<pk>/', views.project_detail_view, name='details'),
    path('<pk>/update', views.project_update_view, name='update'),
    path('<pk>/delete', views.project_delete_view, name='delete'),
    path('<pk>/apply', views.application_create_view, name='apply'),
    path('applicant/<pk>/hire', views.application_accept_view, name='hire'),
    path('applicant/<pk>/deny', views.application_deny_view, name='deny'),
    # path('<pk>/update/', views.ProjectEditView.as_view(), name='update'),
    # path('<pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
]

# project search might just be main project index page.
# search view goes here. list view goes to main project index. 
# no pk necessary. context info will handle that.