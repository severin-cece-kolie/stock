"""
Vues du module Paramètres : entreprise, sécurité (changement de mot
de passe), sauvegarde locale (export JSON complet de la base — via
dumpdata Django, ce qui fonctionne quel que soit le moteur de base de
données configuré, MySQL compris).
"""
import io
import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import redirect, render

from accounts.forms import PasswordChangeSimpleForm
from audit.utils import log_action
from core.permissions import MANAGE_USERS, role_required

from .forms import CompanySettingsForm
from .models import CompanySettings


@login_required
def index(request):
    company = CompanySettings.get_solo()
    can_manage = request.user.role in MANAGE_USERS or request.user.role == 'admin'

    company_form = CompanySettingsForm(instance=company)
    password_form = PasswordChangeSimpleForm(user=request.user)

    if request.method == 'POST':
        section = request.POST.get('section')

        if section == 'company' and can_manage:
            company_form = CompanySettingsForm(request.POST, request.FILES, instance=company)
            if company_form.is_valid():
                company_form.save()
                log_action(request, 'Modification paramètres', 'settings', "Informations de l'entreprise mises à jour")
                messages.success(request, "✅ Informations de l'entreprise mises à jour.")
                return redirect('settings_app:index')

        elif section == 'password':
            password_form = PasswordChangeSimpleForm(request.POST, user=request.user)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data['new_password1'])
                request.user.save(update_fields=['password'])
                update_session_auth_hash(request, request.user)
                log_action(request, 'Modification paramètres', 'settings', 'Mot de passe modifié')
                messages.success(request, "✅ Mot de passe modifié avec succès.")
                return redirect('settings_app:index')

    return render(request, 'settings_app/index.html', {
        'company_form': company_form,
        'password_form': password_form,
        'can_manage': can_manage,
        'tab': request.GET.get('tab', 'company'),
    })


@role_required(*MANAGE_USERS)
def backup_download(request):
    """Sauvegarde locale complète de la base au format JSON (section 17)."""
    buffer = io.StringIO()
    call_command(
        'dumpdata',
        exclude=['contenttypes', 'auth.permission', 'sessions.session', 'admin.logentry'],
        indent=2, stdout=buffer,
    )
    log_action(request, 'Sauvegarde', 'settings', 'Sauvegarde locale de la base téléchargée')

    filename = f"stockmanager_backup_{datetime.now():%Y%m%d_%H%M%S}.json"
    response = HttpResponse(buffer.getvalue(), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
