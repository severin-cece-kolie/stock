"""
Dashboard — KPI et graphique réels (SVG généré côté serveur, fidèle
au design de la maquette Stitch, comme demandé).
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from audit.models import AuditLog
from core.charts import bar_heights_percent, line_chart_svg
from products.models import Product
from sales.models import Sale, SaleItem


@login_required
def index(request):
    today = timezone.localdate()
    start = today - timedelta(days=13)

    products = Product.objects.all()
    low_stock_qs = [p for p in products if p.is_low_stock or p.is_out_of_stock]
    low_stock_count = len(low_stock_qs)
    inventory_value = sum((p.stock_value for p in products), Decimal('0'))

    month_start = today.replace(day=1)
    sales_this_month = Sale.objects.filter(date__date__gte=month_start, status=Sale.Status.COMPLETED).count()
    revenue_this_month = Sale.objects.filter(date__date__gte=month_start, status=Sale.Status.COMPLETED).aggregate(t=Sum('total'))['t'] or Decimal('0')

    # Comparaison avec le mois précédent (pour le badge de tendance)
    prev_month_end = month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)
    revenue_prev_month = Sale.objects.filter(
        date__date__gte=prev_month_start, date__date__lte=prev_month_end, status=Sale.Status.COMPLETED
    ).aggregate(t=Sum('total'))['t'] or Decimal('0')
    if revenue_prev_month > 0:
        revenue_trend_pct = round(float((revenue_this_month - revenue_prev_month) / revenue_prev_month) * 100)
    else:
        revenue_trend_pct = None  # pas de référence pour calculer une évolution

    daily_totals, day_labels = [], []
    for i in range(14):
        day = start + timedelta(days=i)
        total = Sale.objects.filter(date__date=day, status=Sale.Status.COMPLETED).aggregate(t=Sum('total'))['t'] or 0
        daily_totals.append(float(total))
        day_labels.append(day.strftime('%d/%m'))
    chart = line_chart_svg(daily_totals or [0, 0])

    top_products = (
        SaleItem.objects.values('product__name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:5]
    )
    max_top_qty = max((p['total_qty'] for p in top_products), default=1)

    # Répartition des ventes par catégorie (30 derniers jours)
    category_sales = (
        SaleItem.objects
        .filter(sale__date__date__gte=today - timedelta(days=29))
        .values('product__category__name')
        .annotate(total=Sum('subtotal'))
        .order_by('-total')[:5]
    )
    cat_labels = [c['product__category__name'] or 'Sans catégorie' for c in category_sales]
    cat_values = [float(c['total'] or 0) for c in category_sales]
    cat_heights = bar_heights_percent(cat_values)
    cat_colors = ['#0058be', '#38bdf8', '#4edea3', '#f59e0b', '#a78bfa']

    return render(request, 'dashboard/index.html', {
        'total_products': products.count(),
        'sales_this_month': sales_this_month,
        'revenue_this_month': revenue_this_month,
        'revenue_trend_pct': revenue_trend_pct,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_qs[:5],
        'inventory_value': inventory_value,
        'chart': chart,
        'day_labels': day_labels,
        'top_products': top_products,
        'max_top_qty': max_top_qty,
        'category_bars': list(zip(cat_labels, cat_values, cat_heights, cat_colors)),
        'recent_activity': AuditLog.objects.select_related('user').all()[:8],
    })
