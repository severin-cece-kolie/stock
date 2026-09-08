"""
Configuration Django utilisée UNIQUEMENT pour la version empaquetée en
.exe (StockManager Desktop). Contrairement à config/settings.py (qui
utilise MySQL/WampServer pour le développement et l'installation
serveur classique), ce fichier :

- utilise SQLite, embarqué directement dans l'exécutable, sans aucune
  dépendance externe (pas de WampServer/MySQL à installer) ;
- stocke la base de données, les médias et la clé secrète dans un
  dossier "data/" à côté de l'exécutable, pour que les données de
  l'utilisateur survivent aux mises à jour de l'application ;
- désactive le mode DEBUG (usage "production locale").
"""
import sys
from pathlib import Path

from .settings import *  # noqa: F401,F403 — on repart de la config commune

# --------------------------------------------------------------------
# Emplacement des données utilisateur (persistant, à côté de l'exe)
# --------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # Exécuté depuis l'exécutable PyInstaller : sys.executable pointe
    # vers StockManager.exe lui-même.
    APP_DIR = Path(sys.executable).resolve().parent
else:
    # Exécuté depuis les sources (pour tester ce mode sans empaqueter)
    APP_DIR = BASE_DIR

DATA_DIR = APP_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------
# Clé secrète : générée une seule fois puis conservée dans data/,
# pour que les sessions ne soient pas invalidées à chaque redémarrage.
# --------------------------------------------------------------------
SECRET_KEY_FILE = DATA_DIR / 'secret.key'
if SECRET_KEY_FILE.exists():
    SECRET_KEY = SECRET_KEY_FILE.read_text(encoding='utf-8').strip()
else:
    from django.core.management.utils import get_random_secret_key
    SECRET_KEY = get_random_secret_key()
    SECRET_KEY_FILE.write_text(SECRET_KEY, encoding='utf-8')

DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# --------------------------------------------------------------------
# Base de données : SQLite autonome
# --------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(DATA_DIR / 'stockmanager.sqlite3'),
    }
}

# --------------------------------------------------------------------
# Médias (logos, avatars, images produits) : persistants dans data/
# --------------------------------------------------------------------
MEDIA_ROOT = DATA_DIR / 'media'
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------
# Fichiers statiques : déjà collectés au moment du build (voir
# build_exe.bat) et embarqués dans l'exécutable par PyInstaller.
# --------------------------------------------------------------------
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    STATIC_ROOT = Path(sys._MEIPASS) / 'staticfiles'
else:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
