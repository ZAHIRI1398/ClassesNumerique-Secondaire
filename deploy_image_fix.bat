@echo off
REM Script de déploiement de la correction d'affichage d'images
REM Auteur: Cascade
REM Date: 2025-08-18

echo ===== DEPLOIEMENT DE LA CORRECTION D'AFFICHAGE D'IMAGES =====
echo.

REM Vérifier si Git est installé
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Git n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Git depuis https://git-scm.com/downloads
    exit /b 1
)

REM Vérifier si les fichiers nécessaires existent
if not exist fix_image_display.py (
    echo [ERREUR] Le fichier fix_image_display.py est manquant
    exit /b 1
)

if not exist app.py (
    echo [ERREUR] Le fichier app.py est manquant
    exit /b 1
)

echo [1/5] Vérification des modifications...
git status

echo.
echo [2/5] Ajout des fichiers au commit...
git add fix_image_display.py app.py DOCUMENTATION_CORRECTION_AFFICHAGE_IMAGES_PRODUCTION.md GUIDE_DEPLOIEMENT_CORRECTION_IMAGES.md verify_image_fix.py migrate_images_to_cloudinary.py

echo.
echo [3/5] Création du commit...
git commit -m "Fix: Correction des problèmes d'affichage d'images en production"

echo.
echo [4/5] Push des modifications vers GitHub...
git push

echo.
echo [5/5] Déploiement terminé avec succès!
echo.
echo ===== PROCHAINES ETAPES =====
echo.
echo 1. Accédez à votre application Railway et vérifiez le déploiement
echo 2. Une fois déployé, exécutez les routes de diagnostic dans cet ordre:
echo    - https://votre-app.railway.app/fix-uploads-directory
echo    - https://votre-app.railway.app/check-image-paths
echo    - https://votre-app.railway.app/create-placeholder-images
echo.
echo 3. Pour une solution permanente, exécutez le script de migration:
echo    python migrate_images_to_cloudinary.py --no-dry-run
echo.
echo Pour plus d'informations, consultez GUIDE_DEPLOIEMENT_CORRECTION_IMAGES.md
echo.

pause
