from django import forms

from products.forms import INPUT, SELECT

from .models import CompanySettings


class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = ['name', 'logo', 'phone', 'email', 'address', 'currency']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT}),
            'phone': forms.TextInput(attrs={'class': INPUT}),
            'email': forms.EmailInput(attrs={'class': INPUT}),
            'address': forms.TextInput(attrs={'class': INPUT}),
            'currency': forms.TextInput(attrs={'class': INPUT}),
        }
