from django import forms

from products.forms import INPUT, SELECT

from .models import Sale


class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=1, initial=1)


class SaleCustomerForm(forms.Form):
    customer = forms.ModelChoiceField(
        queryset=None, required=False, label='Client',
        widget=forms.Select(attrs={'class': SELECT}),
    )

    def __init__(self, *args, **kwargs):
        from customers.models import Customer
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.all()
