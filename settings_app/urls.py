from django.urls import path

from . import views

app_name = 'settings_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('sauvegarde/telecharger/', views.backup_download, name='backup_download'),
]
