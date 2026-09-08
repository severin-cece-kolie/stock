from django.contrib import admin

from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('reference', 'customer', 'total', 'status', 'date', 'user')
    list_filter = ('status', 'date')
    search_fields = ('reference',)
    inlines = [SaleItemInline]
