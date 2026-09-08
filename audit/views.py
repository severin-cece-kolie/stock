import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .models import AuditLog


@login_required
def index(request):
    logs = AuditLog.objects.select_related('user').all()

    query = request.GET.get('q', '').strip()
    if query:
        logs = logs.filter(description__icontains=query)

    module = request.GET.get('module', '')
    if module:
        logs = logs.filter(module=module)

    return render(request, 'audit/index.html', {
        'logs': logs[:200],
        'query': query,
        'selected_module': module,
        'modules': AuditLog.objects.values_list('module', flat=True).distinct(),
    })


@login_required
def export_csv(request):
    logs = AuditLog.objects.select_related('user').all()[:1000]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historique.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Utilisateur', 'Action', 'Module', 'Description', 'Adresse IP'])
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            str(log.user) if log.user else '—',
            log.action, log.module, log.description, log.ip_address or '',
        ])
    return response
