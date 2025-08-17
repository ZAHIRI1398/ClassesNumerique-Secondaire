@echo off
REM Script pour vérifier les routes en production

echo ===============================================================
echo IMPORTANT: Remplacez l'URL ci-dessous par l'URL de votre application
echo ===============================================================

REM Remplacez cette URL par l'URL de votre application en production
set PRODUCTION_APP_URL=https://web-production-9a047.up.railway.app

echo.
echo Configuration de la variable d'environnement...
echo URL de l'application: %PRODUCTION_APP_URL%
echo.

echo Exécution du script de vérification des routes...
python check_routes_production.py

echo.
echo Appuyez sur une touche pour quitter...
pause
