from django import forms

from products.forms import INPUT

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nom du client'}),
            'phone': forms.TextInput(attrs={'class': INPUT, 'placeholder': '+224 6XX XX XX XX'}),
            'email': forms.EmailInput(attrs={'class': INPUT, 'placeholder': 'client@email.com'}),
            'address': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Adresse'}),
        }
