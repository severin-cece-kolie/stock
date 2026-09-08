"""
URLs du module 'dashboard'.
La page d'accueil (/) sert de point d'entrée après connexion.
"""
from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
]
