"""
Configuration Django pour le projet StockManager (Kamsar Street).

Toutes les valeurs sensibles sont lues depuis le fichier .env
(voir .env.example) grâce à python-decouple. Aucun secret n'est
codé en dur dans ce fichier.
"""

from pathlib import Path
from decouple import config, Csv

# --------------------------------------------------------------------
# Chemins de base
# --------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------
# Sécurité
# --------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-changeme-please-set-a-real-key-in-env')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# --------------------------------------------------------------------
# Applications installées
# --------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librairies tierces
    'widget_tweaks',

    # Applications métier (StockManager / Kamsar Street)
    'core',
    'accounts',
    'products',
    'inventory',
    'sales',
    'suppliers',
    'customers',
    'reports',
    'audit',
    'dashboard',
    'settings_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware maison : consigne automatiquement les actions
    # importantes dans audit_logs (voir section 16 du cahier des charges)
    'audit.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Rend le nom/logo/devise de l'entreprise disponibles
                # dans TOUS les templates (sidebar, topbar, paramètres...)
                'settings_app.context_processors.company_settings',

                # Alertes de stock faible pour la cloche de notifications
                'core.context_processors.low_stock_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --------------------------------------------------------------------
# Base de données — MySQL via WampServer
# --------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='stockmanager_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# --------------------------------------------------------------------
# Hébergement en ligne : la plupart des hébergeurs cloud (Render,
# Railway, Heroku...) fournissent une base de données via une seule
# variable DATABASE_URL, plutôt que DB_NAME/DB_USER/etc séparément.
# Si elle est présente, elle prend le pas sur la config MySQL/WampServer
# ci-dessus — le reste du fichier ne change pas.
# --------------------------------------------------------------------
_database_url = config('DATABASE_URL', default='')
if _database_url:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(_database_url, conn_max_age=600)

# --------------------------------------------------------------------
# Authentification
# --------------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'accounts:login'

# --------------------------------------------------------------------
# Internationalisation
# --------------------------------------------------------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------
# Fichiers statiques et médias
# --------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# Si collectstatic n'a pas été exécuté (oubli, ou build incomplet), sert
# les fichiers non hashés plutôt que de planter en 500 sur chaque page.
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------
# Paramètres métier globaux (valeurs de secours ; la source de vérité
# reste la table settings_app.CompanySettings modifiable via l'UI)
# --------------------------------------------------------------------
COMPANY_NAME_DEFAULT = config('COMPANY_NAME', default='Kamsar Street')
COMPANY_CURRENCY_DEFAULT = config('COMPANY_CURRENCY', default='GNF')

# --------------------------------------------------------------------
# Messages (correspondance avec les toasts Tailwind de la maquette)
# --------------------------------------------------------------------
from django.contrib.messages import constants as messages_constants  # noqa: E402

MESSAGE_TAGS = {
    messages_constants.SUCCESS: 'success',
    messages_constants.ERROR: 'error',
    messages_constants.WARNING: 'warning',
    messages_constants.INFO: 'info',
}

# --------------------------------------------------------------------
# Gestion des erreurs (section 9 du cahier des charges)
# --------------------------------------------------------------------
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

# --------------------------------------------------------------------
# Hébergement en ligne : domaines autorisés à envoyer des formulaires
# (obligatoire avec Django dès qu'on est servi en HTTPS derrière un
# nom de domaine). Ex. dans le .env de production :
# CSRF_TRUSTED_ORIGINS=https://stockmanager-kamsarstreet.onrender.com
# --------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

# --------------------------------------------------------------------
# Sécurité HTTPS — activée UNIQUEMENT en production (DEBUG=False),
# jamais en local, pour ne pas casser le développement en http://
# --------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
    if SECURE_HSTS_SECONDS:
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
    # La plupart des hébergeurs (Render, Railway...) placent l'app
    # derrière un proxy HTTPS : cet en-tête indique à Django que la
    # requête est bien sécurisée malgré une connexion interne en http.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
