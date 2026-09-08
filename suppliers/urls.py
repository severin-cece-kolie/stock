from django.urls import path

from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.index, name='index'),
    path('ajouter/', views.supplier_create, name='create'),
    path('<int:pk>/modifier/', views.supplier_update, name='update'),
    path('<int:pk>/supprimer/', views.supplier_delete, name='delete'),
    path('categories/ajouter/', views.category_create, name='category_create'),
    path('categories/<int:pk>/modifier/', views.category_update, name='category_update'),
    path('categories/<int:pk>/supprimer/', views.category_delete, name='category_delete'),
]
