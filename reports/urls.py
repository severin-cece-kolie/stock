from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.index, name='index'),
    path('stock.csv', views.export_stock_csv, name='export_stock_csv'),
    path('stock.pdf', views.export_stock_pdf, name='export_stock_pdf'),
    path('stock.xlsx', views.export_stock_excel, name='export_stock_excel'),
]
