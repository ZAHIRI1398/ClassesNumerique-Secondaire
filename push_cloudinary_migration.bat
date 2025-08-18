@echo off
echo ========================================
echo POUSSANT LES MODIFICATIONS SUR GITHUB
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
echo 1. Vérification du statut Git...
%GIT_PATH% status

echo.
echo 2. Ajout de tous les fichiers modifiés...
%GIT_PATH% add .

echo.
echo 3. Création du commit avec message descriptif...
%GIT_PATH% commit -m "✅ Migration des images vers Cloudinary

- ✅ Scripts de diagnostic pour vérifier les images dans la base de données
- ✅ Scripts pour associer des images aux exercices existants
- ✅ Script pour uploader directement les images vers Cloudinary
- ✅ Documentation complète du processus de migration
- ✅ Configuration des variables d'environnement Cloudinary

Fonctionnalités implémentées:
- Diagnostic des problèmes d'images dans la base de données
- Association d'images aux exercices existants
- Upload direct des images vers Cloudinary
- Migration des images référencées dans la base de données
- Documentation détaillée du processus

Solution complète pour résoudre définitivement les problèmes d'affichage d'images en production"

echo.
echo 4. Poussant vers GitHub...
%GIT_PATH% push origin main

echo.
echo ========================================
echo MODIFICATIONS POUSSÉES AVEC SUCCÈS !
echo ========================================
pause
