from django.contrib import admin

from .models import StockEntry, StockOutput


@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ('product', 'supplier', 'quantity', 'date', 'user')
    list_filter = ('date',)


@admin.register(StockOutput)
class StockOutputAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reason', 'date', 'user')
    list_filter = ('reason', 'date')
