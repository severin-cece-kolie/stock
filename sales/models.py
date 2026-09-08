"""
Ventes.

Une Sale peut contenir plusieurs SaleItem (section 12 du cahier des
charges). La création complète (vente + lignes + décrément de stock)
est orchestrée par Sale.create_with_items(), enveloppée dans une
transaction : si un seul article a un stock insuffisant, RIEN n'est
enregistré.
"""
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from products.models import InsufficientStockError


class Sale(models.Model):
    class Status(models.TextChoices):
        COMPLETED = 'completed', 'Complétée'
        CANCELLED = 'cancelled', 'Annulée'

    reference = models.CharField('Référence', max_length=30, unique=True, blank=True)
    customer = models.ForeignKey('customers.Customer', verbose_name='Client', on_delete=models.PROTECT, null=True, blank=True)
    total = models.DecimalField('Total', max_digits=14, decimal_places=2, default=0)
    status = models.CharField('Statut', max_length=10, choices=Status.choices, default=Status.COMPLETED)
    date = models.DateTimeField('Date', default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Vendeur', on_delete=models.PROTECT)

    class Meta:
        db_table = 'sales'
        verbose_name = 'Vente'
        verbose_name_plural = 'Ventes'
        ordering = ['-date']

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            last = Sale.objects.filter(reference__startswith=f'V-{year}-').order_by('-id').first()
            next_number = 1
            if last:
                try:
                    next_number = int(last.reference.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    next_number = Sale.objects.filter(reference__startswith=f'V-{year}-').count() + 1
            self.reference = f'V-{year}-{next_number:03d}'
        super().save(*args, **kwargs)

    @staticmethod
    @transaction.atomic
    def create_with_items(*, customer, user, cart_items):
        """
        cart_items : liste de dicts {'product': Product, 'quantity': int}
        Crée la vente, ses lignes, et décrémente le stock de chaque
        produit via Product.adjust_stock(). Toute la transaction est
        annulée si un seul article a un stock insuffisant.
        """
        sale = Sale.objects.create(customer=customer, user=user, total=0)
        total = 0
        for item in cart_items:
            product = item['product']
            quantity = item['quantity']
            unit_price = product.selling_price
            subtotal = unit_price * quantity
            SaleItem.objects.create(
                sale=sale, product=product, quantity=quantity,
                unit_price=unit_price, subtotal=subtotal,
            )
            product.adjust_stock(-quantity)  # lève InsufficientStockError si besoin -> rollback
            total += subtotal
        sale.total = total
        sale.save(update_fields=['total'])
        return sale


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, verbose_name='Vente', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', verbose_name='Produit', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField('Quantité')
    unit_price = models.DecimalField('Prix unitaire', max_digits=12, decimal_places=2)
    subtotal = models.DecimalField('Sous-total', max_digits=14, decimal_places=2)

    class Meta:
        db_table = 'sale_items'
        verbose_name = 'Ligne de vente'
        verbose_name_plural = 'Lignes de vente'

    def __str__(self):
        return f"{self.product} × {self.quantity}"
