@echo off
echo Deploiement des corrections pour les abonnements de type 'Trial'...

REM Ajout des fichiers modifies
echo.
echo === AJOUT DES FICHIERS MODIFIES ===
git add production_code/ClassesNumerique-Secondaire-main/payment_routes.py
git add admin_fix_subscriptions.py

REM Creation du commit
echo.
echo === CREATION DU COMMIT ===
git commit -m "Fix: Inclusion des abonnements de type Trial et trial dans la detection des ecoles"

REM Push vers le depot distant
echo.
echo === PUSH VERS LE DEPOT DISTANT ===
git push

echo.
echo Deploiement termine! Les modifications seront appliquees automatiquement par Railway.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul
