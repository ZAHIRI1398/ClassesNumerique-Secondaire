@echo off
echo === SCRIPT DE DEPLOIEMENT MANUEL DU TEMPLATE SELECT_SCHOOL ===

echo === CREATION D'UNE SAUVEGARDE ===
mkdir backup_select_school_manual_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
copy production_code\ClassesNumerique-Secondaire-main\templates\payment\*.* backup_select_school_manual_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%\

echo === VERIFICATION DU REPERTOIRE DE DESTINATION ===
if not exist production_code\ClassesNumerique-Secondaire-main\templates\payment mkdir production_code\ClassesNumerique-Secondaire-main\templates\payment

echo === COPIE DU TEMPLATE ===
copy templates\payment\select_school.html production_code\ClassesNumerique-Secondaire-main\templates\payment\

echo === VERIFICATION DE LA COPIE ===
if exist production_code\ClassesNumerique-Secondaire-main\templates\payment\select_school.html (
    echo Template copie avec succes!
) else (
    echo ERREUR: Le template n'a pas ete copie correctement!
    exit /b 1
)

echo === COMMIT ET PUSH VERS GITHUB ===
cd production_code\ClassesNumerique-Secondaire-main
git add templates/payment/select_school.html
git commit -m "Ajout du template select_school.html manquant"
git push
cd ..\..

echo === DEPLOIEMENT MANUEL VERS RAILWAY ===
echo.
echo INSTRUCTIONS POUR DEPLOYER MANUELLEMENT SUR RAILWAY:
echo 1. Connectez-vous a votre compte Railway
echo 2. Accedez au projet ClassesNumerique
echo 3. Cliquez sur "Deploy" ou "Redeploy" pour le service web
echo 4. Attendez que le deploiement soit termine
echo.
echo Une fois le deploiement termine, executez verify_select_school_template.py pour verifier que tout fonctionne correctement.
