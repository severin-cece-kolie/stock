"""
Vue de connexion personnalisée : ajoute la gestion réelle de
"Se souvenir de moi" (durée de session) par-dessus la LoginView
standard de Django.
"""
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from audit.utils import log_action
from core.permissions import MANAGE_USERS, role_required

from .forms import UserCreateForm, UserUpdateForm
from .models import User


class StockManagerLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.POST.get('remember-me'):
            # Session conservée 30 jours (SESSION_COOKIE_AGE)
            self.request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            # Session expire à la fermeture du navigateur
            self.request.session.set_expiry(0)
        return response


@role_required(*MANAGE_USERS)
def user_list(request):
    users = User.objects.all().order_by('username')
    query = request.GET.get('q', '').strip()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'query': query,
        'form': UserCreateForm(),
        'role_labels': dict(User.Role.choices),
    })


@role_required(*MANAGE_USERS)
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_action(request, 'Création utilisateur', 'accounts', f"Utilisateur « {user.username} » créé ({user.get_role_display()})")
            messages.success(request, f"✅ Utilisateur « {user.username} » créé avec succès.")
        else:
            errors = ' '.join(f"{f}: {e[0]}" for f, e in form.errors.items())
            messages.error(request, f"❌ {errors or 'Le formulaire contient des erreurs.'}")
    return redirect('accounts:user_list')


@role_required(*MANAGE_USERS)
def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            log_action(request, 'Modification utilisateur', 'accounts', f"Utilisateur « {user_obj.username} » modifié")
            messages.success(request, f"✅ Utilisateur « {user_obj.username} » modifié avec succès.")
            return redirect('accounts:user_list')
    else:
        form = UserUpdateForm(instance=user_obj)
    return render(request, 'accounts/user_form.html', {'form': form, 'user_obj': user_obj})


@role_required(*MANAGE_USERS)
def user_toggle_active(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user_obj == request.user:
            messages.error(request, "❌ Vous ne pouvez pas désactiver votre propre compte.")
        else:
            user_obj.is_active = not user_obj.is_active
            user_obj.save(update_fields=['is_active'])
            state = 'activé' if user_obj.is_active else 'désactivé'
            log_action(request, 'Modification utilisateur', 'accounts', f"Compte « {user_obj.username} » {state}")
            messages.success(request, f"✅ Compte « {user_obj.username} » {state}.")
    return redirect('accounts:user_list')
