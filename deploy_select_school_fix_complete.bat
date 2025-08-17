@echo off
echo ===================================================
echo Deploiement complet de la correction select-school
echo ===================================================
echo.

echo [1/8] Verification des fichiers...
if not exist fix_payment_select_school.py (
    echo ERREUR: Le fichier fix_payment_select_school.py est manquant!
    exit /b 1
)
if not exist diagnose_select_school_route.py (
    echo ERREUR: Le fichier diagnose_select_school_route.py est manquant!
    exit /b 1
)
if not exist integrate_select_school_fix.py (
    echo ERREUR: Le fichier integrate_select_school_fix.py est manquant!
    exit /b 1
)
if not exist templates\fix_payment_select_school.html (
    echo ERREUR: Le template fix_payment_select_school.html est manquant!
    exit /b 1
)
if not exist integrate_app_select_school_fix.py (
    echo ERREUR: Le fichier integrate_app_select_school_fix.py est manquant!
    exit /b 1
)
echo Tous les fichiers necessaires sont presents.
echo.

echo [2/8] Creation d'une sauvegarde...
if not exist backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%\ (
    mkdir backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%
)
if exist app.py (
    copy app.py backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%\app.py.bak
    echo Sauvegarde de app.py creee
)
if exist production_code\ClassesNumerique-Secondaire-main\app.py (
    copy production_code\ClassesNumerique-Secondaire-main\app.py backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%\app_production.py.bak
    echo Sauvegarde de app.py (production) creee
)
echo.

echo [3/8] Preparation des fichiers pour le commit...
echo Copie des fichiers vers le repertoire templates...
if not exist templates\payment\ (
    mkdir templates\payment
)
copy templates\fix_payment_select_school.html templates\payment\fix_payment_select_school.html
echo.

echo [4/8] Copie des fichiers vers le repertoire de production...
if not exist production_code\ClassesNumerique-Secondaire-main\templates\payment\ (
    mkdir production_code\ClassesNumerique-Secondaire-main\templates\payment
)
copy fix_payment_select_school.py production_code\ClassesNumerique-Secondaire-main\
copy diagnose_select_school_route.py production_code\ClassesNumerique-Secondaire-main\
copy integrate_select_school_fix.py production_code\ClassesNumerique-Secondaire-main\
copy integrate_app_select_school_fix.py production_code\ClassesNumerique-Secondaire-main\
copy templates\fix_payment_select_school.html production_code\ClassesNumerique-Secondaire-main\templates\payment\
echo.

echo [5/8] Integration de la correction dans app.py...
python integrate_app_select_school_fix.py production_code\ClassesNumerique-Secondaire-main\app.py
if %errorlevel% neq 0 (
    echo ERREUR: Impossible d'integrer la correction dans app.py.
    exit /b 1
)
echo.

echo [6/8] Ajout des fichiers au commit Git...
git add fix_payment_select_school.py
git add diagnose_select_school_route.py
git add integrate_select_school_fix.py
git add integrate_app_select_school_fix.py
git add templates\fix_payment_select_school.html
git add templates\payment\fix_payment_select_school.html
git add production_code\ClassesNumerique-Secondaire-main\fix_payment_select_school.py
git add production_code\ClassesNumerique-Secondaire-main\diagnose_select_school_route.py
git add production_code\ClassesNumerique-Secondaire-main\integrate_select_school_fix.py
git add production_code\ClassesNumerique-Secondaire-main\integrate_app_select_school_fix.py
git add production_code\ClassesNumerique-Secondaire-main\templates\payment\fix_payment_select_school.html
git add production_code\ClassesNumerique-Secondaire-main\app.py
git add DOCUMENTATION_CORRECTION_SELECT_SCHOOL_ROUTE.md
git add test_select_school_fix.py
git add deploy_select_school_fix.bat
git add deploy_select_school_fix_complete.bat
echo.

echo [7/8] Creation du commit...
git commit -m "Fix: Correction de l'erreur 500 sur la route /payment/select-school avec diagnostic et integration"
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de creer le commit Git.
    exit /b 1
)
echo.

echo [8/8] Push vers le depot distant...
git push
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de pousser les modifications vers le depot distant.
    exit /b 1
)
echo.

echo ===================================================
echo Deploiement termine avec succes!
echo ===================================================
echo.
echo Pour verifier la correction en production:
echo 1. Connectez-vous a l'interface d'administration Railway
echo 2. Verifiez que le deploiement s'est termine avec succes
echo 3. Accedez a l'URL: https://votre-domaine.up.railway.app/diagnose/select-school-route
echo 4. Analysez les resultats du diagnostic
echo 5. Testez la version corrigee via: https://votre-domaine.up.railway.app/fix-payment/select-school
echo.
echo Appuyez sur une touche pour quitter...
pause > nul
