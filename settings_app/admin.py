from django.contrib import admin

from .models import CompanySettings


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'email', 'phone')

    def has_add_permission(self, request):
        return not CompanySettings.objects.exists()
