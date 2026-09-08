from django import forms

from products.forms import INPUT, SELECT

from .models import User


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class': INPUT}))
    password2 = forms.CharField(label='Confirmation du mot de passe', widget=forms.PasswordInput(attrs={'class': INPUT}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT, 'placeholder': "Nom d'utilisateur"}),
            'first_name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': INPUT, 'placeholder': 'email@kamsarstreet.gn'}),
            'phone': forms.TextInput(attrs={'class': INPUT, 'placeholder': '+224 6XX XX XX XX'}),
            'role': forms.Select(attrs={'class': SELECT}),
        }

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Les deux mots de passe ne correspondent pas.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'role', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT}),
            'last_name': forms.TextInput(attrs={'class': INPUT}),
            'email': forms.EmailInput(attrs={'class': INPUT}),
            'phone': forms.TextInput(attrs={'class': INPUT}),
            'role': forms.Select(attrs={'class': SELECT}),
        }


class PasswordChangeSimpleForm(forms.Form):
    """Utilisée dans Paramètres > Sécurité pour que l'utilisateur change son propre mot de passe."""
    current_password = forms.CharField(label='Mot de passe actuel', widget=forms.PasswordInput(attrs={'class': INPUT}))
    new_password1 = forms.CharField(label='Nouveau mot de passe', widget=forms.PasswordInput(attrs={'class': INPUT}))
    new_password2 = forms.CharField(label='Confirmer le nouveau mot de passe', widget=forms.PasswordInput(attrs={'class': INPUT}))

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data['current_password']
        if self.user and not self.user.check_password(pwd):
            raise forms.ValidationError("Le mot de passe actuel est incorrect.")
        return pwd

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('new_password1'), cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            self.add_error('new_password2', 'Les deux mots de passe ne correspondent pas.')
        if p1 and len(p1) < 8:
            self.add_error('new_password1', 'Le mot de passe doit contenir au moins 8 caractères.')
        return cleaned
