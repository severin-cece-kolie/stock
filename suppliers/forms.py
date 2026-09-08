from django import forms

from products.forms import INPUT, SELECT, TEXTAREA
from products.models import Category

from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'email', 'address', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nom du fournisseur'}),
            'phone': forms.TextInput(attrs={'class': INPUT, 'placeholder': '+224 6XX XX XX XX'}),
            'email': forms.EmailInput(attrs={'class': INPUT, 'placeholder': 'contact@fournisseur.gn'}),
            'address': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Adresse'}),
            'status': forms.Select(attrs={'class': SELECT}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 3, 'placeholder': 'Description (optionnelle)'}),
        }
