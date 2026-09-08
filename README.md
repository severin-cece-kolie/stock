# StockManager — Kamsar Street

Logiciel de gestion de stock développé pour **Kamsar Street**
(« Gestion intelligente de votre stock »).

## Stack technique

- Backend : Python 3 / Django 5.1
- Base de données : MySQL (via WampServer en local)
- Frontend : templates Django + Tailwind CSS (CDN)
- Exports : PDF (reportlab), Excel (openpyxl), CSV

## Installation locale (Windows + WampServer)

1. Démarrer WampServer et créer une base de données vide, par exemple `stockmanager_db`
   (dans phpMyAdmin : *Bases de données* → *Créer une base*).

2. Ouvrir un terminal dans le dossier du projet :

   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copier `.env.example` en `.env` et renseigner vos identifiants MySQL :

   ```
   copy .env.example .env
   ```

   Éditez `.env` et remplissez `DB_NAME`, `DB_USER`, `DB_PASSWORD` (généralement
   `root` sans mot de passe pour une installation WampServer par défaut),
   ainsi qu'une `SECRET_KEY` unique (n'importe quelle longue chaîne aléatoire).

4. Appliquer les migrations :

   ```
   python manage.py migrate
   ```

5. Créer un compte administrateur :

   ```
   python manage.py createsuperuser
   ```

   *(ou, pour des données de démonstration prêtes à l'emploi — voir plus bas)*

6. Lancer le serveur :

   ```
   python manage.py runserver
   ```

7. Ouvrir votre navigateur sur **http://127.0.0.1:8000**

## Données de démonstration

Pour peupler rapidement l'application avec des utilisateurs, produits,
catégories et fournisseurs de test :

```
python manage.py seed_demo_data
```

Comptes créés (mot de passe commun : `ChangeMoi123!`, **à changer en
production** dans *Paramètres > Sécurité*) :

| Utilisateur | Rôle           |
|-------------|----------------|
| severin     | Administrateur |
| mamadou     | Gestionnaire   |
| fatou       | Vendeur        |

## Rôles et permissions

- **Administrateur** : accès complet (y compris Utilisateurs et Paramètres).
- **Gestionnaire** : produits, stock, fournisseurs, catégories, rapports.
- **Vendeur** : ventes, clients, consultation des produits.
- **Consultation** : lecture seule sur l'ensemble de l'application.

Les permissions sont vérifiées **côté serveur** (décorateur `role_required`),
pas seulement en masquant des boutons côté interface.

## Fonctionnalités principales

- Authentification sécurisée (mots de passe hashés, protection CSRF)
- Gestion des produits, catégories, fournisseurs, clients
- Entrées / sorties de stock avec verrouillage anti-incohérence
  (impossible de descendre sous 0, même en cas d'accès concurrent)
- Ventes multi-produits avec décrément de stock transactionnel
- Journal d'audit automatique (connexions, créations, modifications, suppressions)
- Rapports avec export CSV / PDF / Excel
- Dashboard avec statistiques réelles et graphique généré côté serveur (SVG)
- Sauvegarde locale de la base au format JSON (*Paramètres > Sauvegarde*)
- Interface d'administration Django complète (`/admin/`)

## Application mobile (PWA) — installation sur iOS

StockManager peut être installé comme une application sur iPhone/iPad,
directement depuis Safari (pas besoin de passer par l'App Store) :

1. Ouvrez l'application dans **Safari** (pas Chrome — le "Ajouter à
   l'écran d'accueil" de Safari est nécessaire sur iOS).
2. Appuyez sur le bouton de partage (icône carrée avec une flèche vers
   le haut).
3. Choisissez **"Sur l'écran d'accueil"**.

Une icône StockManager apparaît alors sur l'écran d'accueil, s'ouvre
en plein écran (sans barre d'adresse), comme une vraie application.

⚠️ Pour que ça fonctionne correctement (et que le mode hors-ligne et
l'installation soient proposés), l'application doit être servie en
**HTTPS** — voir la section hébergement ci-dessous. En local
(`127.0.0.1`), l'installation à l'écran d'accueil ne fonctionne pas de
façon fiable sur iOS.

## Hébergement en ligne (pour un accès partagé admin/gestionnaire)

Par défaut, StockManager tourne en local (WampServer) ou en exécutable
autonome (`.exe`, SQLite isolé par appareil). Pour que **plusieurs
personnes** (administrateur, gestionnaire...) travaillent sur les
**mêmes données**, partagées en temps réel, il faut héberger
l'application sur un serveur unique accessible en ligne.

Le projet est prêt pour un hébergement de type **Render.com**
(offre gratuite disponible, HTTPS automatique — nécessaire pour la PWA) :

1. Poussez le projet sur un dépôt Git (GitHub, GitLab...).
2. Sur [render.com](https://render.com), créez un **Web Service** à
   partir de ce dépôt.
3. Ajoutez une base de données PostgreSQL depuis Render (gratuite) —
   Render fournit automatiquement une variable `DATABASE_URL`, que
   l'application utilise directement sans configuration supplémentaire.
4. Dans les variables d'environnement du service, définissez :
   - `SECRET_KEY` : une valeur longue et aléatoire
   - `DEBUG` : `False`
   - `ALLOWED_HOSTS` : le domaine fourni par Render (ex. `stockmanager-kamsarstreet.onrender.com`)
   - `CSRF_TRUSTED_ORIGINS` : `https://` + ce même domaine
5. Commande de build : `pip install -r requirements.txt -r requirements-hosting.txt && python manage.py collectstatic --noinput`
6. Commande de démarrage : déjà définie dans `Procfile` (migrations automatiques + Gunicorn).

Une fois déployé, admin et gestionnaire se connectent simplement à
l'URL Render depuis n'importe quel appareil (ordinateur, téléphone,
PWA installée) et voient exactement les mêmes données.

*(Si vous préférez un autre hébergeur avec du MySQL plutôt que
PostgreSQL — Railway, un VPS, etc. — le projet fonctionne aussi tel
quel : donnez simplement une `DATABASE_URL` au format
`mysql://utilisateur:motdepasse@hote:3306/nom_base` et gardez
`requirements.txt` sans `requirements-hosting.txt`.)*

## Empaquetage en exécutable Windows (StockManager.exe)

L'application peut être empaquetée en un **exécutable Windows autonome**,
sans aucune dépendance externe (pas de WampServer, pas de MySQL, pas
même besoin d'installer Python sur la machine finale). Ce mode utilise
**SQLite** au lieu de MySQL — la base de données est un simple fichier,
créé et géré automatiquement.

### Construire l'exécutable

Sur une machine Windows avec Python installé :

```
build_exe.bat
```

Ce script :
1. installe les dépendances nécessaires (dans un environnement virtuel dédié, `build_venv/`) ;
2. collecte les fichiers statiques (CSS, favicon...) ;
3. construit `dist\StockManager.exe` avec PyInstaller.

La première construction prend quelques minutes. Le résultat est un
seul fichier : `dist\StockManager.exe`.

### Utiliser l'exécutable

Double-cliquez sur `StockManager.exe` (vous pouvez le copier n'importe
où, y compris sur une clé USB ou un autre PC Windows) :

- Au premier lancement, l'application crée automatiquement un dossier
  `data\` à côté de l'exécutable (base de données SQLite, médias, clé
  de sécurité) et un compte administrateur par défaut :
  **`admin` / `Admin1234!`** — à changer immédiatement dans
  *Paramètres > Sécurité*.
- Le navigateur par défaut s'ouvre automatiquement sur l'application.
- Une fenêtre de console reste ouverte tant que l'application tourne ;
  la fermer arrête StockManager.
- Vos données (`data\`) sont conservées d'un lancement à l'autre, et
  survivent au remplacement de l'exécutable par une version plus
  récente (ne supprimez pas ce dossier).

### Différence avec l'installation "développeur" (MySQL/WampServer)

Les deux modes cohabitent dans le même projet et n'interfèrent pas :

| | Installation développeur | Exécutable StockManager.exe |
|---|---|---|
| Base de données | MySQL (WampServer) | SQLite (fichier local) |
| Lancement | `python manage.py runserver` | Double-clic sur l'exe |
| Fichier de config | `config/settings.py` | `config/settings_desktop.py` |
| Dépendances | `requirements.txt` | `requirements-desktop.txt` |

## Logo de l'entreprise

Le logo peut être téléversé depuis *Paramètres > Entreprise* — il s'affichera
automatiquement dans la sidebar, sur la page de connexion et dans les paramètres.

## Empaquetage futur en exécutable Windows

Le projet est structuré pour faciliter un futur empaquetage en `.exe`
(configuration séparée du code via `.env`, pas de dépendance cloud
obligatoire). Cette étape n'a pas encore été réalisée — l'application
fonctionne pour l'instant comme un serveur Django local classique.
