"""
Rend les informations de l'entreprise (nom, logo, devise) disponibles
dans TOUS les templates — sidebar, topbar, page Login, paramètres.
"""
from .models import CompanySettings


def company_settings(request):
    company = CompanySettings.get_solo()
    return {
        'company': company,
        'company_name': company.name,
        'company_currency': company.currency,
        'company_logo_url': company.logo.url if company.logo else None,
    }
