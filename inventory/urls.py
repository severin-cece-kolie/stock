from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.index, name='index'),
    path('entrees/ajouter/', views.entry_create, name='entry_create'),
    path('sorties/ajouter/', views.output_create, name='output_create'),
]
