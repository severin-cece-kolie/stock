from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from audit.utils import log_action
from core.permissions import MANAGE_CATALOG, role_required

from .forms import ProductForm
from .models import Category, Product


@login_required
def product_list(request):
    products = Product.objects.select_related('category', 'supplier').all()

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(reference__icontains=query) | Q(barcode__icontains=query)
        )

    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)

    stock_state = request.GET.get('stock', '')
    if stock_state == 'out':
        products = products.filter(stock_quantity=0)
    elif stock_state == 'low':
        products = [p for p in products if p.is_low_stock]
    elif stock_state == 'available':
        products = products.exclude(stock_quantity=0)

    if not isinstance(products, list):
        products = list(products)

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'products/list.html', {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'query': query,
        'selected_category': category_id,
        'selected_stock_state': stock_state,
        'can_manage': request.user.role in MANAGE_CATALOG or request.user.role == 'admin',
    })


@role_required(*MANAGE_CATALOG)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            log_action(request, 'Création produit', 'products', f"Produit « {product.name} » créé")
            messages.success(request, f"✅ Produit « {product.name} » créé avec succès.")
            return redirect('products:index')
    else:
        form = ProductForm()
    return render(request, 'products/form.html', {'form': form, 'is_edit': False})


@role_required(*MANAGE_CATALOG)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            log_action(request, 'Modification produit', 'products', f"Produit « {product.name} » modifié")
            messages.success(request, f"✅ Produit « {product.name} » modifié avec succès.")
            return redirect('products:index')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/form.html', {'form': form, 'is_edit': True, 'product': product})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category', 'supplier'), pk=pk)
    return render(request, 'products/detail.html', {
        'product': product,
        'entries': product.stock_entries.select_related('supplier', 'user').order_by('-date')[:10],
        'outputs': product.stock_outputs.select_related('user').order_by('-date')[:10],
        'sale_items': product.saleitem_set.select_related('sale').order_by('-sale__date')[:10],
        'can_manage': request.user.role in MANAGE_CATALOG or request.user.role == 'admin',
    })


@role_required(*MANAGE_CATALOG)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        try:
            product.delete()
            log_action(request, 'Suppression produit', 'products', f"Produit « {name} » supprimé")
            messages.success(request, f"🗑 Produit « {name} » supprimé.")
        except Exception:
            messages.error(request, "❌ Impossible de supprimer ce produit : il est référencé dans des mouvements de stock ou des ventes.")
    return redirect('products:index')


# Alias utilisé par la sidebar (namespace products -> index = liste)
index = product_list
