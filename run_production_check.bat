@echo off
REM Script pour exécuter le diagnostic en production

echo ===============================================================
echo IMPORTANT: Remplacez les valeurs ci-dessous par vos identifiants réels
echo ===============================================================

REM Remplacez les valeurs suivantes par vos identifiants réels de production
set PRODUCTION_DATABASE_URL=postgresql://username:password@hostname:port/database_name
set PRODUCTION_APP_URL=https://votre-application.up.railway.app

echo.
echo Configuration des variables d'environnement...
echo URL de la base de données: %PRODUCTION_DATABASE_URL%
echo URL de l'application: %PRODUCTION_APP_URL%
echo.

echo Exécution du script de diagnostic...
python check_production_subscriptions.py

echo.
echo Appuyez sur une touche pour quitter...
pause
