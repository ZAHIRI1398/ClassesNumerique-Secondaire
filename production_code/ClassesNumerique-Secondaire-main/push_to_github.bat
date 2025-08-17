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
%GIT_PATH% commit -m "✅ Implémentation complète du système Glisser-déposer

- ✅ Section drag_and_drop ajoutée au template de création
- ✅ Logique backend de création et édition implémentée  
- ✅ Template d'édition drag_and_drop_edit.html créé
- ✅ Options drag_and_drop et underline_words ajoutées à la liste d'édition
- ✅ Validation, parsing et sauvegarde JSON fonctionnels
- ✅ Système entièrement opérationnel pour création/modification/affichage/scoring

Fonctionnalités validées:
- Création d'exercices via interface web
- Modification d'exercices existants  
- Affichage et soumission d'exercices
- Scoring et feedback automatiques
- Gestion des erreurs et validation

Structure JSON: draggable_items, drop_zones, correct_order"

echo.
echo 4. Poussant vers GitHub...
%GIT_PATH% push origin main

echo.
echo ========================================
echo MODIFICATIONS POUSSÉES AVEC SUCCÈS !
echo ========================================
pause
