@echo off
echo Deploiement du script de verification des abonnements...

REM Ajout des fichiers modifies
echo.
echo === AJOUT DES FICHIERS MODIFIES ===
git add production_code/ClassesNumerique-Secondaire-main/verify_subscriptions.py

REM Creation du commit
echo.
echo === CREATION DU COMMIT ===
git commit -m "Add: Script de verification des abonnements en production"

REM Push vers le depot distant
echo.
echo === PUSH VERS LE DEPOT DISTANT ===
git push

echo.
echo Deploiement termine! Les modifications seront appliquees automatiquement par Railway.
echo Pour executer le script en production, utilisez la commande:
echo python verify_subscriptions.py
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul
