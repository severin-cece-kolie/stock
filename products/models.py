"""
Modèles Produits & Catégories.

La logique de mouvement de stock est centralisée dans
Product.adjust_stock() : c'est le SEUL point d'entrée qui doit
modifier stock_quantity, pour garantir qu'on ne puisse jamais
atteindre un stock négatif (section 7 du cahier des charges).
"""
from django.conf import settings
from django.db import models, transaction
from django.db.models import F


class InsufficientStockError(Exception):
    """Levée quand une sortie/vente dépasserait le stock disponible."""
    pass


class Category(models.Model):
    name = models.CharField('Nom', max_length=120, unique=True)
    description = models.TextField('Description', blank=True)
    created_at = models.DateTimeField('Créée le', auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Actif'
        INACTIVE = 'inactive', 'Inactif'

    name = models.CharField('Nom', max_length=200)
    reference = models.CharField('Référence', max_length=60, unique=True)
    barcode = models.CharField('Code-barres', max_length=64, unique=True, blank=True, null=True)
    category = models.ForeignKey(
        Category, verbose_name='Catégorie',
        on_delete=models.PROTECT, related_name='products',
        null=True, blank=True,
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier', verbose_name='Fournisseur',
        on_delete=models.PROTECT, related_name='products',
        null=True, blank=True,
    )
    purchase_price = models.DecimalField('Prix d\'achat', max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField('Prix de vente', max_digits=12, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField('Stock actuel', default=0)
    minimum_stock = models.PositiveIntegerField('Seuil minimum', default=0)
    description = models.TextField('Description', blank=True)
    image = models.ImageField('Image', upload_to='products/', blank=True, null=True)
    status = models.CharField('Statut', max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.reference})"

    @property
    def is_low_stock(self):
        return self.minimum_stock > 0 and 0 < self.stock_quantity <= self.minimum_stock

    @property
    def is_out_of_stock(self):
        return self.stock_quantity == 0

    @property
    def stock_value(self):
        return self.stock_quantity * self.purchase_price

    @transaction.atomic
    def adjust_stock(self, delta):
        """
        Ajuste le stock de `delta` (positif = entrée, négatif =
        sortie/vente) de façon atomique et verrouillée (select_for_update)
        pour éviter toute condition de course entre deux ventes
        simultanées. Lève InsufficientStockError si le résultat serait
        négatif — dans ce cas AUCUNE écriture n'est effectuée.
        """
        locked = Product.objects.select_for_update().get(pk=self.pk)
        new_quantity = locked.stock_quantity + delta
        if new_quantity < 0:
            raise InsufficientStockError(
                f"Stock insuffisant pour « {locked.name} » : "
                f"disponible {locked.stock_quantity}, demandé {-delta}."
            )
        locked.stock_quantity = new_quantity
        locked.save(update_fields=['stock_quantity', 'updated_at'])
        self.stock_quantity = new_quantity
        return self.stock_quantity
