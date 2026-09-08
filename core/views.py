from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def csrf_failure(request, reason=""):
    return render(request, '403_csrf.html', status=403)


def service_worker(request):
    """
    Sert le service worker à la RACINE du site (/sw.js), condition
    indispensable pour qu'il ait la portée ("scope") sur toute
    l'application et pas seulement sur /static/js/.
    """
    path = Path(settings.BASE_DIR) / 'static' / 'js' / 'service-worker.js'
    content = path.read_text(encoding='utf-8')
    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response


def manifest(request):
    """Sert le manifest PWA à la racine (/manifest.json)."""
    path = Path(settings.BASE_DIR) / 'static' / 'manifest.json'
    content = path.read_text(encoding='utf-8')
    return HttpResponse(content, content_type='application/manifest+json')


def offline(request):
    """Page de secours affichée par le service worker quand l'appareil est hors ligne."""
    return render(request, 'offline.html')
