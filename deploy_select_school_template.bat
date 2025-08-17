@echo off
echo === SCRIPT DE DEPLOIEMENT DU TEMPLATE SELECT_SCHOOL ===

echo === CREATION D'UNE SAUVEGARDE ===
mkdir backup_select_school_template_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
copy production_code\ClassesNumerique-Secondaire-main\templates\payment\*.* backup_select_school_template_%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%\

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

echo === DEPLOIEMENT TERMINE ===
echo Le template a ete deploye avec succes et sera automatiquement mis a jour sur Railway.
