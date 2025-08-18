@echo off
echo === SCRIPT DE DEPLOIEMENT DE LA CORRECTION PAIEMENT ENSEIGNANT ===

echo === CREATION D'UNE SAUVEGARDE ===
mkdir backup_payment_fix_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
copy production_code\ClassesNumerique-Secondaire-main\payment_service.py backup_payment_fix_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%\
copy production_code\ClassesNumerique-Secondaire-main\payment_routes.py backup_payment_fix_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%\

echo === COPIE DES FICHIERS DE CORRECTION ===
copy fix_payment_teacher_subscription.py production_code\ClassesNumerique-Secondaire-main\
copy integrate_payment_fix.py production_code\ClassesNumerique-Secondaire-main\

echo === VERIFICATION DE LA COPIE ===
if exist production_code\ClassesNumerique-Secondaire-main\fix_payment_teacher_subscription.py (
    echo Fichier fix_payment_teacher_subscription.py copie avec succes!
) else (
    echo ERREUR: Le fichier fix_payment_teacher_subscription.py n'a pas ete copie correctement!
    exit /b 1
)

if exist production_code\ClassesNumerique-Secondaire-main\integrate_payment_fix.py (
    echo Fichier integrate_payment_fix.py copie avec succes!
) else (
    echo ERREUR: Le fichier integrate_payment_fix.py n'a pas ete copie correctement!
    exit /b 1
)

echo === MODIFICATION DU FICHIER APP.PY POUR INTEGRER LA CORRECTION ===
echo from integrate_payment_fix import integrate_fix >> production_code\ClassesNumerique-Secondaire-main\app.py
echo integrate_fix() >> production_code\ClassesNumerique-Secondaire-main\app.py

echo === COMMIT ET PUSH VERS GITHUB ===
cd production_code\ClassesNumerique-Secondaire-main
git add fix_payment_teacher_subscription.py
git add integrate_payment_fix.py
git add app.py
git commit -m "✅ Correction du problème de paiement pour les enseignants sans école

- ✅ Correction de l'erreur lors de la création de la session de paiement
- ✅ Ajout de logs détaillés pour faciliter le diagnostic
- ✅ Gestion robuste des erreurs avec try/except
- ✅ Intégration transparente avec l'application existante"

git push origin main
cd ..\..

echo === DEPLOIEMENT MANUEL VERS RAILWAY ===
echo.
echo INSTRUCTIONS POUR DEPLOYER MANUELLEMENT SUR RAILWAY:
echo 1. Connectez-vous a votre compte Railway
echo 2. Accedez au projet ClassesNumerique
echo 3. Cliquez sur "Deploy" ou "Redeploy" pour le service web
echo 4. Attendez que le deploiement soit termine
echo.
echo Une fois le deploiement termine, verifiez que le paiement fonctionne correctement.
