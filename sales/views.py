"""
Vues du module Ventes.

La page "Nouvelle Vente" utilise un panier stocké en session
(request.session['cart'] = {product_id: quantity}) : chaque ajout
fait un aller-retour serveur (pas de JS complexe requis), et la
validation finale du stock est faite de façon atomique dans
Sale.create_with_items() (section 12 : transactions MySQL/Django
pour éviter les incohérences).
"""
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from audit.utils import log_action
from core.permissions import MANAGE_SALES, role_required
from customers.models import Customer
from products.models import InsufficientStockError, Product

from .models import Sale, SaleItem

CART_SESSION_KEY = 'cart'


@login_required
def sale_list(request):
    sales = Sale.objects.select_related('customer', 'user').prefetch_related('items')

    today = timezone.localdate()
    month_start = today.replace(day=1)

    kpis = {
        'today_count': Sale.objects.filter(date__date=today, status=Sale.Status.COMPLETED).count(),
        'month_count': Sale.objects.filter(date__date__gte=month_start, status=Sale.Status.COMPLETED).count(),
        'revenue': Sale.objects.filter(status=Sale.Status.COMPLETED).aggregate(t=Sum('total'))['t'] or Decimal('0'),
        'transactions': Sale.objects.filter(status=Sale.Status.COMPLETED).count(),
    }

    return render(request, 'sales/list.html', {
        'sales': sales.order_by('-date')[:100],
        'kpis': kpis,
        'can_manage': request.user.role in MANAGE_SALES or request.user.role == 'admin',
    })


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale.objects.select_related('customer', 'user').prefetch_related('items__product'), pk=pk)
    return render(request, 'sales/detail.html', {'sale': sale})


def _get_cart(request):
    return request.session.get(CART_SESSION_KEY, {})


def _save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def _cart_lines(cart):
    lines = []
    total = Decimal('0')
    products = Product.objects.in_bulk([int(pid) for pid in cart.keys()])
    for pid_str, qty in cart.items():
        product = products.get(int(pid_str))
        if not product:
            continue
        subtotal = product.selling_price * qty
        total += subtotal
        lines.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
    return lines, total


@role_required(*MANAGE_SALES)
def new_sale(request):
    cart = _get_cart(request)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            product_id = request.POST.get('product_id')
            try:
                quantity = int(request.POST.get('quantity', 1))
            except ValueError:
                quantity = 1
            product = Product.objects.filter(pk=product_id).first()
            if product and quantity > 0:
                current = cart.get(str(product.pk), 0)
                if current + quantity > product.stock_quantity:
                    messages.error(request, f"❌ Stock insuffisant pour « {product.name} » (disponible : {product.stock_quantity}).")
                else:
                    cart[str(product.pk)] = current + quantity
                    _save_cart(request, cart)
            return redirect('sales:new')

        elif action == 'scan':
            barcode = (request.POST.get('barcode') or '').strip()
            product = Product.objects.filter(barcode=barcode).first() if barcode else None
            if not product:
                messages.error(request, f"❌ Aucun produit trouvé pour le code-barres « {barcode} ».")
            else:
                current = cart.get(str(product.pk), 0)
                if current + 1 > product.stock_quantity:
                    messages.error(request, f"❌ Stock insuffisant pour « {product.name} » (disponible : {product.stock_quantity}).")
                else:
                    cart[str(product.pk)] = current + 1
                    _save_cart(request, cart)
                    messages.success(request, f"✅ « {product.name} » ajouté au panier.")
            return redirect('sales:new')

        elif action == 'remove':
            product_id = request.POST.get('product_id')
            cart.pop(str(product_id), None)
            _save_cart(request, cart)
            return redirect('sales:new')

        elif action == 'clear':
            _save_cart(request, {})
            return redirect('sales:new')

        elif action == 'checkout':
            lines, total = _cart_lines(cart)
            if not lines:
                messages.error(request, "❌ Le panier est vide.")
                return redirect('sales:new')

            customer_id = request.POST.get('customer')
            customer = Customer.objects.filter(pk=customer_id).first() if customer_id else None

            try:
                sale = Sale.create_with_items(
                    customer=customer,
                    user=request.user,
                    cart_items=[{'product': l['product'], 'quantity': l['quantity']} for l in lines],
                )
            except InsufficientStockError as exc:
                messages.error(request, f"❌ {exc}")
                return redirect('sales:new')

            _save_cart(request, {})
            log_action(request, 'Vente', 'sales', f"Vente {sale.reference} enregistrée pour un total de {sale.total}")
            messages.success(request, f"✅ Vente {sale.reference} enregistrée avec succès.")
            return redirect('sales:detail', pk=sale.pk)

    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(status=Product.Status.ACTIVE)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(reference__icontains=query))
    products = products.order_by('name')[:30]

    lines, total = _cart_lines(cart)

    return render(request, 'sales/new.html', {
        'products': products,
        'query': query,
        'cart_lines': lines,
        'cart_total': total,
        'customers': Customer.objects.all(),
    })
