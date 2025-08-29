@echo off
echo ========================================
echo DEPLOIEMENT DES CORRECTIONS D'AFFICHAGE D'IMAGES
echo ========================================

REM Définir le chemin de Git
set GIT_PATH="C:\Program Files\Git\bin\git.exe"

REM Vérifier si Git existe
if not exist %GIT_PATH% (
    echo Git non trouvé à %GIT_PATH%
    echo Essayons avec git dans le PATH...
    set GIT_PATH=git
)

echo.
echo 1. Exécution du script de préparation Python...
python deploy_image_fix_railway.py

echo.
echo 2. Vérification du statut Git...
%GIT_PATH% status

echo.
echo 3. Ajout des fichiers nécessaires...
%GIT_PATH% add fix_image_paths.py app.py DOCUMENTATION_CORRECTION_AFFICHAGE_IMAGES_COMPLETE.md GUIDE_DEPLOIEMENT_CORRECTION_IMAGES_COMPLET.md GUIDE_DEPLOIEMENT_RAILWAY_CLOUDINARY.md

echo.
echo 4. Création du commit avec message descriptif...
%GIT_PATH% commit -m "Correction complete affichage images"

echo.
echo 5. Poussant vers GitHub...
%GIT_PATH% push origin main

echo.
echo ========================================
echo MODIFICATIONS POUSSÉES AVEC SUCCÈS !
echo ========================================
echo.
echo INSTRUCTIONS POUR RAILWAY:
echo 1. Connectez-vous à votre dashboard Railway
echo 2. Sélectionnez votre projet
echo 3. Cliquez sur "Deploy" pour déclencher un nouveau déploiement
echo 4. Une fois déployé, accédez aux routes suivantes:
echo    - /fix-template-paths
echo    - /sync-image-paths
echo    - /check-image-consistency
echo    - /create-simple-placeholders
echo.
echo N'oubliez pas de configurer les variables d'environnement Cloudinary dans Railway:
echo - CLOUDINARY_CLOUD_NAME
echo - CLOUDINARY_API_KEY
echo - CLOUDINARY_API_SECRET
echo ========================================
pause
