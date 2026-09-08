from django.db import models


class Supplier(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Actif'
        INACTIVE = 'inactive', 'Inactif'

    name = models.CharField('Nom du fournisseur', max_length=200)
    phone = models.CharField('Téléphone', max_length=40, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.CharField('Adresse', max_length=255, blank=True)
    status = models.CharField('Statut', max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)

    class Meta:
        db_table = 'suppliers'
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['name']

    def __str__(self):
        return self.name
