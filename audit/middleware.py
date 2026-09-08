"""
Middleware d'audit.

Pour l'instant ce middleware ne fait que passer la requête (no-op).
La logique d'enregistrement automatique dans audit_logs (connexion,
déconnexion, création/modification/suppression, etc. — voir section 16
du cahier des charges) sera implémentée lors du développement du
module `audit`.
"""


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
