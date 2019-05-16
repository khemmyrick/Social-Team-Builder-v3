from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    # url(r'new/', views.CreateProjectView.as_view(), name='new'),
    path('search/', views.ProjectListView.as_view(), name='search'),
    path('<pk>/', views.ProjectDetailView.as_view(), name='details'),
    # path('<pk>/edit/', views.ProjectEditView.as_view(), name='edit'),
    # path('<pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
]

# project search might just be main project index page.
# search view goes here. list view goes to main project index. 
# no pk necessary. context info will handle that.