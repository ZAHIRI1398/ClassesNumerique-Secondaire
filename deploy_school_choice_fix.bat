@echo off
echo Deploiement des corrections pour le probleme de choix d'ecole...

REM Ajout des fichiers modifies
echo.
echo === AJOUT DES FICHIERS MODIFIES ===
git add diagnostic_school_choice.py
git add fix_school_choice.py
git add app.py
git add DOCUMENTATION_CORRECTION_CHOIX_ECOLE.md
git add templates/diagnostic/school_choice.html
git add templates/fix/school_choice_result.html

REM Creation du commit
echo.
echo === CREATION DU COMMIT ===
git commit -m "Fix: Correction du probleme de choix d'ecole en production"

REM Push vers le depot distant
echo.
echo === PUSH VERS LE DEPOT DISTANT ===
git push

echo.
echo Deploiement termine! Les modifications seront appliquees automatiquement par Railway.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul
