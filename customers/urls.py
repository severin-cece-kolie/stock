from django.urls import path

from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.index, name='index'),
    path('ajouter/', views.customer_create, name='create'),
    path('<int:pk>/supprimer/', views.customer_delete, name='delete'),
]
