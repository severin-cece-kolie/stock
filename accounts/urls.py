"""
URLs du module 'accounts'.
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('connexion/', views.StockManagerLoginView.as_view(), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('utilisateurs/', views.user_list, name='user_list'),
    path('utilisateurs/ajouter/', views.user_create, name='user_create'),
    path('utilisateurs/<int:pk>/modifier/', views.user_update, name='user_update'),
    path('utilisateurs/<int:pk>/basculer/', views.user_toggle_active, name='user_toggle_active'),
]
