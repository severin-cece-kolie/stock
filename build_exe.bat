@echo off
setlocal

echo ============================================
echo   StockManager - Construction de l'executable
echo ============================================
echo.

REM --- 1. Environnement virtuel dedie a la construction ---
if not exist build_venv (
    echo Creation de l'environnement de build...
    python -m venv build_venv
)
call build_venv\Scripts\activate.bat

echo Installation des dependances...
pip install --upgrade pip >nul
pip install -r requirements-desktop.txt
if errorlevel 1 (
    echo.
    echo ERREUR : l'installation des dependances a echoue.
    pause
    exit /b 1
)

REM --- 2. Collecte des fichiers statiques (indispensable, DEBUG=False) ---
echo.
echo Collecte des fichiers statiques...
set DJANGO_SETTINGS_MODULE=config.settings_desktop
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo.
    echo ERREUR : la collecte des fichiers statiques a echoue.
    pause
    exit /b 1
)

REM --- 3. Nettoyage des builds precedents ---
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM --- 4. Construction de l'executable avec PyInstaller ---
echo.
echo Construction de l'executable (cela peut prendre plusieurs minutes)...
pyinstaller --noconfirm --onefile --name StockManager --console ^
  --add-data "staticfiles;staticfiles" ^
  --add-data "templates;templates" ^
  --add-data "accounts;accounts" ^
  --add-data "products;products" ^
  --add-data "inventory;inventory" ^
  --add-data "sales;sales" ^
  --add-data "suppliers;suppliers" ^
  --add-data "customers;customers" ^
  --add-data "reports;reports" ^
  --add-data "audit;audit" ^
  --add-data "dashboard;dashboard" ^
  --add-data "settings_app;settings_app" ^
  --add-data "core;core" ^
  --add-data "config;config" ^
  --hidden-import whitenoise ^
  --hidden-import whitenoise.middleware ^
  --hidden-import whitenoise.storage ^
  --hidden-import waitress ^
  --hidden-import decouple ^
  --hidden-import PIL ^
  --hidden-import reportlab ^
  --hidden-import openpyxl ^
  --hidden-import widget_tweaks ^
  --hidden-import widget_tweaks.templatetags.widget_tweaks ^
  desktop\launcher.py

if errorlevel 1 (
    echo.
    echo ERREUR : la construction de l'executable a echoue.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Termine !
echo   L'executable se trouve dans : dist\StockManager.exe
echo ============================================
echo.
echo Vous pouvez copier StockManager.exe n'importe ou sur un PC Windows
echo et le lancer directement (double-clic) : aucune installation de
echo Python, Django, WampServer ou MySQL n'est necessaire.
echo.
pause
