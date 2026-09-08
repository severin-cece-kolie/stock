"""
Context processor global : alertes de stock faible/rupture, affichées
dans la cloche de notifications de la topbar sur TOUTES les pages.

Les alertes sont calculées à la volée depuis l'état réel du stock
(pas de table de notifications à part) : dès qu'un produit est
réapprovisionné, il disparaît automatiquement de la liste.
"""


def low_stock_notifications(request):
    if not request.user.is_authenticated:
        return {}

    from products.models import Product

    products = Product.objects.filter(status=Product.Status.ACTIVE).only(
        'id', 'name', 'stock_quantity', 'minimum_stock'
    )
    alerts = [p for p in products if p.is_low_stock or p.is_out_of_stock]
    alerts.sort(key=lambda p: p.stock_quantity)

    return {
        'low_stock_alerts': alerts[:8],
        'low_stock_count': len(alerts),
    }
