from django import forms
from django.utils import timezone

from products.forms import INPUT, INPUT_MONO, SELECT, TEXTAREA

from .models import StockEntry, StockOutput


class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = ['product', 'supplier', 'quantity', 'purchase_price', 'date', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': SELECT}),
            'supplier': forms.Select(attrs={'class': SELECT}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_MONO + ' text-right', 'min': 1}),
            'purchase_price': forms.NumberInput(attrs={'class': INPUT_MONO + ' text-right', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'note': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Note (optionnelle)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date'].initial = timezone.localdate()


class StockOutputForm(forms.ModelForm):
    class Meta:
        model = StockOutput
        fields = ['product', 'quantity', 'reason', 'date', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': SELECT}),
            'quantity': forms.NumberInput(attrs={'class': INPUT_MONO + ' text-right', 'min': 1}),
            'reason': forms.Select(attrs={'class': SELECT}),
            'date': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
            'note': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Note (optionnelle)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date'].initial = timezone.localdate()
