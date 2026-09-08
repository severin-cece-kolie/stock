"""
Modèle utilisateur personnalisé.

StockManager utilise un modèle User personnalisé dès le départ (bonne
pratique Django) pour pouvoir y ajouter les champs métier (rôle,
téléphone, avatar...) sans migration lourde plus tard.

Le détail des rôles/permissions (section 9 du cahier des charges :
Administrateur / Gestionnaire / Vendeur / Consultation) sera implémenté
lors du développement complet du module accounts, via des Groups
Django standards + ce champ `role` à titre d'étiquette d'affichage.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        MANAGER = 'manager', 'Gestionnaire'
        SELLER = 'seller', 'Vendeur'
        VIEWER = 'viewer', 'Consultation'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
    )
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.get_full_name() or self.username
