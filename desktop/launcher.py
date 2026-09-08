"""
Point d'entrée de StockManager Desktop (.exe).

Ce script :
1. configure Django en mode "desktop" (SQLite autonome, voir
   config/settings_desktop.py) ;
2. applique automatiquement les migrations au premier lancement (et à
   chaque mise à jour) — l'utilisateur n'a jamais à taper de commande ;
3. crée un compte administrateur par défaut si la base est neuve ;
4. démarre un serveur web local (Waitress, adapté à un usage desktop,
   plus robuste que le serveur de développement Django) ;
5. ouvre automatiquement le navigateur par défaut sur l'application.

Fermer la fenêtre de la console (ou l'icône dans la barre des tâches)
arrête l'application.
"""
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Permet de lancer ce script aussi bien empaqueté (PyInstaller) que
# directement depuis les sources, pour pouvoir le tester sans exe.
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys._MEIPASS)
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_desktop')

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402

HOST = '127.0.0.1'
PORT = 8000
URL = f'http://{HOST}:{PORT}/'


def prepare_database():
    """Applique les migrations et crée un compte admin par défaut si besoin."""
    print("StockManager — préparation de la base de données...")
    call_command('migrate', interactive=False, verbosity=0)

    from accounts.models import User
    if not User.objects.filter(is_superuser=True).exists():
        print("Aucun compte administrateur trouvé — création du compte par défaut.")
        User.objects.create_superuser(
            username='admin',
            email='admin@kamsarstreet.gn',
            password='Admin1234!',
            first_name='Administrateur',
            role='admin',
        )
        print("→ Identifiant : admin / Mot de passe : Admin1234!")
        print("  (à changer immédiatement dans Paramètres > Sécurité)")


def run_server():
    from waitress import serve
    from config.wsgi import application
    serve(application, host=HOST, port=PORT, threads=6)


def main():
    prepare_database()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Laisse le serveur démarrer avant d'ouvrir le navigateur
    time.sleep(1.5)
    print(f"StockManager est démarré sur {URL}")
    print("Laissez cette fenêtre ouverte tant que vous utilisez l'application.")
    webbrowser.open(URL)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt de StockManager.")


if __name__ == '__main__':
    main()
