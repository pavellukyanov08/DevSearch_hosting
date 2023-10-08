from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),
    path('projects/<int:pk>/', views.project, name='project'),
    path('create-project/', views.create_project, name='create-project'),
    path('update-project/<pk>', views.update_project, name='update-project'),
    path('delete-project/<pk>', views.delete_project, name='delete-project'),
]
