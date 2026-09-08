"""
Fonction utilitaire pour consigner une action dans audit_logs
(section 16 du cahier des charges).
"""
def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, module, description=''):
    from .models import AuditLog
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        module=module,
        description=description,
        ip_address=_client_ip(request),
    )
