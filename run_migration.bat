@echo off
REM Script pour exécuter la migration des images vers Cloudinary
REM Auteur: Cascade
REM Date: 2025-08-18

echo ===== MIGRATION DES IMAGES VERS CLOUDINARY =====
echo.

REM Charger les variables d'environnement depuis .env.cloudinary
for /f "tokens=*" %%a in (.env.cloudinary) do (
    set %%a
)

echo Variables d'environnement Cloudinary chargées
echo.

REM Exécuter le script de migration en mode simulation d'abord
echo Exécution en mode simulation (dry-run)...
python migrate_images_to_cloudinary.py

echo.
echo Pour exécuter la migration réelle, utilisez:
echo python migrate_images_to_cloudinary.py --no-dry-run
echo.

pause
