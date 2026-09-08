"""
URLs racine du projet StockManager.

Chaque module métier possède son propre urls.py inclus ici avec un
espace de noms (namespace), pour correspondre à la sidebar de la
maquette Stitch :
Dashboard / Products / In-Out (inventory) / Sales / Categories &
Suppliers / Users / Reports / History (audit) / Settings
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # PWA : servies à la racine (obligatoire pour le service worker)
    path('sw.js', core_views.service_worker, name='service_worker'),
    path('manifest.json', core_views.manifest, name='manifest'),
    path('hors-ligne/', core_views.offline, name='offline'),

    path('', include('dashboard.urls', namespace='dashboard')),
    path('comptes/', include('accounts.urls', namespace='accounts')),
    path('produits/', include('products.urls', namespace='products')),
    path('stock/', include('inventory.urls', namespace='inventory')),
    path('ventes/', include('sales.urls', namespace='sales')),
    path('fournisseurs/', include('suppliers.urls', namespace='suppliers')),
    path('clients/', include('customers.urls', namespace='customers')),
    path('rapports/', include('reports.urls', namespace='reports')),
    path('historique/', include('audit.urls', namespace='audit')),
    path('parametres/', include('settings_app.urls', namespace='settings_app')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
