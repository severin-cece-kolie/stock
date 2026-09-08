"""
Mouvements de stock : entrées et sorties.

Toute écriture de stock_quantity passe exclusivement par
Product.adjust_stock() (voir products/models.py) — jamais d'écriture
directe ici, pour garantir la cohérence.
"""
from django.conf import settings
from django.db import models, transaction

from products.models import InsufficientStockError, Product


class StockEntry(models.Model):
    product = models.ForeignKey(Product, verbose_name='Produit', on_delete=models.PROTECT, related_name='stock_entries')
    supplier = models.ForeignKey('suppliers.Supplier', verbose_name='Fournisseur', on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField('Quantité')
    purchase_price = models.DecimalField('Prix d\'achat', max_digits=12, decimal_places=2, default=0)
    date = models.DateField('Date')
    note = models.CharField('Note', max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Utilisateur', on_delete=models.PROTECT)
    created_at = models.DateTimeField('Enregistrée le', auto_now_add=True)

    class Meta:
        db_table = 'stock_entries'
        verbose_name = 'Entrée de stock'
        verbose_name_plural = 'Entrées de stock'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Entrée #{self.pk} — {self.product} (+{self.quantity})"

    @transaction.atomic
    def apply(self):
        """Applique l'entrée : augmente le stock du produit concerné."""
        self.product.adjust_stock(self.quantity)


class StockOutput(models.Model):
    class Reason(models.TextChoices):
        DAMAGE = 'damage', 'Produit endommagé'
        LOSS = 'loss', 'Perte'
        INTERNAL_USE = 'internal_use', 'Usage interne'
        CORRECTION = 'correction', 'Correction d\'inventaire'
        OTHER = 'other', 'Autre'

    product = models.ForeignKey(Product, verbose_name='Produit', on_delete=models.PROTECT, related_name='stock_outputs')
    quantity = models.PositiveIntegerField('Quantité')
    reason = models.CharField('Motif', max_length=20, choices=Reason.choices, default=Reason.OTHER)
    date = models.DateField('Date')
    note = models.CharField('Note', max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Utilisateur', on_delete=models.PROTECT)
    created_at = models.DateTimeField('Enregistrée le', auto_now_add=True)

    class Meta:
        db_table = 'stock_outputs'
        verbose_name = 'Sortie de stock'
        verbose_name_plural = 'Sorties de stock'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Sortie #{self.pk} — {self.product} (-{self.quantity})"

    @transaction.atomic
    def apply(self):
        """Applique la sortie : diminue le stock. Lève InsufficientStockError si impossible."""
        self.product.adjust_stock(-self.quantity)
