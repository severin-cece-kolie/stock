from django.urls import path

from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='index'),
    path('nouvelle/', views.new_sale, name='new'),
    path('<int:pk>/', views.sale_detail, name='detail'),
]
