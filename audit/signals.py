"""
Connexion / déconnexion consignées automatiquement via les signaux
d'authentification de Django (section 16 : "connexion", "déconnexion").
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .utils import log_action


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    log_action(request, 'Connexion', 'accounts', f"{user.get_full_name() or user.username} s'est connecté(e)")


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user:
        log_action(request, 'Déconnexion', 'accounts', f"{user.get_full_name() or user.username} s'est déconnecté(e)")
