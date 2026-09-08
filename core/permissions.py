"""
Permissions par rôle.

Le cahier des charges définit 4 rôles : Administrateur, Gestionnaire,
Vendeur, Consultation (accounts.models.User.Role). Plutôt que de
masquer uniquement des boutons côté template, chaque vue de
création/modification/suppression est protégée côté serveur avec le
décorateur `role_required`.

Un Administrateur a toujours accès à tout.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """
    Autorise l'accès si request.user.role est dans `roles`, ou si
    l'utilisateur est Administrateur (accès complet toujours garanti).
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user_role = getattr(request.user, 'role', None)
            if user_role == 'admin' or user_role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Vous n'avez pas la permission d'accéder à cette page.")
        return _wrapped
    return decorator


# Groupes de rôles réutilisés dans les vues des différents modules
MANAGE_CATALOG = ('admin', 'manager')          # produits, catégories, fournisseurs
MANAGE_STOCK = ('admin', 'manager')            # entrées / sorties de stock
MANAGE_SALES = ('admin', 'manager', 'seller')  # ventes, clients
MANAGE_USERS = ('admin',)                      # utilisateurs, paramètres
VIEW_REPORTS = ('admin', 'manager')            # rapports
