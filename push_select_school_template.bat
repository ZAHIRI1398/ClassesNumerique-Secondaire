@echo off
echo ========================================
echo POUSSANT LE TEMPLATE SELECT_SCHOOL VERS GITHUB
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
cd production_code\ClassesNumerique-Secondaire-main
%GIT_PATH% status

echo.
echo 2. Ajout du template select_school.html...
%GIT_PATH% add templates/payment/select_school.html

echo.
echo 3. Création du commit avec message descriptif...
%GIT_PATH% commit -m "✅ Ajout du template select_school.html manquant

- ✅ Correction de l'erreur 500 sur la route /payment/select-school
- ✅ Permet aux enseignants de sélectionner une école avec abonnement actif
- ✅ Résout le problème de template manquant en production

Cette correction permet aux enseignants de s'associer correctement à une école
ayant un abonnement actif, ce qui est essentiel pour le flux d'abonnement."

echo.
echo 4. Poussant vers GitHub...
%GIT_PATH% push origin main

echo.
echo ========================================
echo TEMPLATE SELECT_SCHOOL POUSSÉ AVEC SUCCÈS !
echo ========================================
cd ..\..
pause
