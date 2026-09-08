from django import forms

from .models import Category, Product

INPUT = ("w-full bg-surface-container-lowest border border-outline-variant "
         "focus:border-secondary focus:ring-1 focus:ring-secondary rounded-lg "
         "px-3 py-2.5 font-body-md text-body-md text-on-surface transition-colors")
INPUT_MONO = INPUT.replace('font-body-md text-body-md', 'font-data-mono text-data-mono')
SELECT = INPUT + " appearance-none"
TEXTAREA = INPUT + " resize-y"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'reference', 'barcode', 'category', 'supplier',
            'purchase_price', 'selling_price',
            'stock_quantity', 'minimum_stock',
            'description', 'image', 'status',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ex: Perceuse sans fil 18V'}),
            'reference': forms.TextInput(attrs={'class': INPUT_MONO, 'placeholder': 'Ex: REF-2026-ABC'}),
            'barcode': forms.TextInput(attrs={'class': INPUT_MONO, 'placeholder': 'Ex: 6191234567890 (scanner ou saisir)'}),
            'category': forms.Select(attrs={'class': SELECT}),
            'supplier': forms.Select(attrs={'class': SELECT}),
            'purchase_price': forms.NumberInput(attrs={'class': INPUT_MONO, 'placeholder': '0.00', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': INPUT_MONO, 'placeholder': '0.00', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': INPUT_MONO + ' text-right', 'placeholder': '0'}),
            'minimum_stock': forms.NumberInput(attrs={'class': INPUT_MONO + ' text-right', 'placeholder': '5'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 4, 'placeholder': 'Description détaillée du produit, caractéristiques techniques...'}),
            'status': forms.Select(attrs={'class': SELECT}),
        }

    def clean_barcode(self):
        barcode = (self.cleaned_data.get('barcode') or '').strip()
        if not barcode:
            return None
        qs = Product.objects.filter(barcode=barcode)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce code-barres est déjà utilisé par un autre produit.")
        return barcode

    def clean_reference(self):
        reference = self.cleaned_data['reference'].strip()
        qs = Product.objects.filter(reference__iexact=reference)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Cette référence est déjà utilisée par un autre produit.")
        return reference


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 3}),
        }
