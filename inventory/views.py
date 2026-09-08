from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from audit.utils import log_action
from core.permissions import MANAGE_STOCK, role_required
from products.models import InsufficientStockError, Product

from .forms import StockEntryForm, StockOutputForm
from .models import StockEntry, StockOutput


@login_required
def index(request):
    tab = request.GET.get('tab', 'entries')
    can_manage = request.user.role in MANAGE_STOCK or request.user.role == 'admin'

    return render(request, 'inventory/index.html', {
        'tab': tab,
        'entries': StockEntry.objects.select_related('product', 'supplier', 'user')[:100],
        'outputs': StockOutput.objects.select_related('product', 'user')[:100],
        'can_manage': can_manage,
        'entry_form': StockEntryForm(),
        'output_form': StockOutputForm(),
    })


@role_required(*MANAGE_STOCK)
def entry_create(request):
    if request.method == 'POST':
        form = StockEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            entry.apply()
            log_action(request, 'Entrée de stock', 'inventory',
                       f"+{entry.quantity} pour « {entry.product.name} »")
            messages.success(request, f"✅ Entrée enregistrée : +{entry.quantity} pour « {entry.product.name} ».")
        else:
            messages.error(request, "❌ Le formulaire contient des erreurs. Vérifiez les champs.")
    return redirect('/stock/')


@role_required(*MANAGE_STOCK)
def output_create(request):
    if request.method == 'POST':
        form = StockOutputForm(request.POST)
        if form.is_valid():
            output = form.save(commit=False)
            output.user = request.user
            product = output.product
            if output.quantity > product.stock_quantity:
                messages.error(
                    request,
                    f"❌ Stock insuffisant pour « {product.name} » : "
                    f"disponible {product.stock_quantity}, demandé {output.quantity}."
                )
            else:
                output.save()
                try:
                    output.apply()
                except InsufficientStockError as exc:
                    output.delete()
                    messages.error(request, f"❌ {exc}")
                else:
                    log_action(request, 'Sortie de stock', 'inventory',
                               f"-{output.quantity} pour « {product.name} » ({output.get_reason_display()})")
                    messages.success(request, f"✅ Sortie enregistrée : -{output.quantity} pour « {product.name} ».")
        else:
            messages.error(request, "❌ Le formulaire contient des erreurs. Vérifiez les champs.")
    return redirect('/stock/?tab=outputs')
