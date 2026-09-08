from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from audit.utils import log_action
from core.permissions import MANAGE_SALES, role_required

from .forms import CustomerForm
from .models import Customer


@login_required
def index(request):
    customers = Customer.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        customers = customers.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query))
    can_manage = request.user.role in MANAGE_SALES or request.user.role == 'admin'
    return render(request, 'customers/index.html', {
        'customers': customers,
        'query': query,
        'can_manage': can_manage,
        'form': CustomerForm(),
    })


@role_required(*MANAGE_SALES)
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            log_action(request, 'Création client', 'customers', f"Client « {customer.name} » créé")
            messages.success(request, f"✅ Client « {customer.name} » créé avec succès.")
        else:
            messages.error(request, "❌ Le formulaire contient des erreurs.")
    return redirect('customers:index')


@role_required(*MANAGE_SALES)
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = customer.name
        try:
            customer.delete()
            log_action(request, 'Suppression client', 'customers', f"Client « {name} » supprimé")
            messages.success(request, f"🗑 Client « {name} » supprimé.")
        except Exception:
            messages.error(request, "❌ Impossible de supprimer : ce client a des ventes associées.")
    return redirect('customers:index')
