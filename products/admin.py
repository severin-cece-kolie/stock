from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference', 'barcode', 'category', 'supplier', 'stock_quantity', 'minimum_stock', 'selling_price', 'status')
    list_filter = ('status', 'category', 'supplier')
    search_fields = ('name', 'reference', 'barcode')
