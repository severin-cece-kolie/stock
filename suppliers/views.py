from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from audit.utils import log_action
from core.permissions import MANAGE_CATALOG, role_required
from products.models import Category

from .forms import CategoryForm, SupplierForm
from .models import Supplier


@login_required
def index(request):
    """Page combinée Fournisseurs & Catégories (2 onglets, comme le Stitch)."""
    tab = request.GET.get('tab', 'suppliers')
    can_manage = request.user.role in MANAGE_CATALOG or request.user.role == 'admin'

    query = request.GET.get('q', '').strip()

    suppliers = Supplier.objects.all()
    if query and tab != 'categories':
        suppliers = suppliers.filter(Q(name__icontains=query) | Q(email__icontains=query))

    categories = Category.objects.all()
    if query and tab == 'categories':
        categories = categories.filter(name__icontains=query)

    return render(request, 'suppliers/index.html', {
        'tab': tab,
        'suppliers': suppliers,
        'categories': categories,
        'query': query,
        'can_manage': can_manage,
        'supplier_form': SupplierForm(),
        'category_form': CategoryForm(),
    })


@role_required(*MANAGE_CATALOG)
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            log_action(request, 'Création fournisseur', 'suppliers', f"Fournisseur « {supplier.name} » créé")
            messages.success(request, f"✅ Fournisseur « {supplier.name} » créé avec succès.")
        else:
            messages.error(request, "❌ Le formulaire contient des erreurs : " + str(form.errors))
    return redirect('/fournisseurs/')


@role_required(*MANAGE_CATALOG)
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            log_action(request, 'Modification fournisseur', 'suppliers', f"Fournisseur « {supplier.name} » modifié")
            messages.success(request, f"✅ Fournisseur « {supplier.name} » modifié avec succès.")
            return redirect('/fournisseurs/')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'supplier': supplier})


@role_required(*MANAGE_CATALOG)
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = supplier.name
        try:
            supplier.delete()
            log_action(request, 'Suppression fournisseur', 'suppliers', f"Fournisseur « {name} » supprimé")
            messages.success(request, f"🗑 Fournisseur « {name} » supprimé.")
        except Exception:
            messages.error(request, "❌ Impossible de supprimer : ce fournisseur est lié à des produits ou des entrées de stock.")
    return redirect('/fournisseurs/')


@role_required(*MANAGE_CATALOG)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            log_action(request, 'Création catégorie', 'products', f"Catégorie « {category.name} » créée")
            messages.success(request, f"✅ Catégorie « {category.name} » créée avec succès.")
        else:
            messages.error(request, "❌ Le formulaire contient des erreurs : " + str(form.errors))
    return redirect('/fournisseurs/?tab=categories')


@role_required(*MANAGE_CATALOG)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            log_action(request, 'Modification catégorie', 'products', f"Catégorie « {category.name} » modifiée")
            messages.success(request, f"✅ Catégorie « {category.name} » modifiée avec succès.")
            return redirect('/fournisseurs/?tab=categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'suppliers/category_form.html', {'form': form, 'category': category})


@role_required(*MANAGE_CATALOG)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        try:
            category.delete()
            log_action(request, 'Suppression catégorie', 'products', f"Catégorie « {name} » supprimée")
            messages.success(request, f"🗑 Catégorie « {name} » supprimée.")
        except Exception:
            messages.error(request, "❌ Impossible de supprimer : cette catégorie est utilisée par des produits.")
    return redirect('/fournisseurs/?tab=categories')
