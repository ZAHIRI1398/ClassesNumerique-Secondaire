@echo off
echo ===================================================
echo Deploiement simplifie de la correction select-school
echo ===================================================
echo.

echo [1/5] Creation d'une sauvegarde...
mkdir backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%
copy app.py backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%\app.py.bak
echo.

echo [2/5] Preparation des fichiers...
if not exist templates\payment mkdir templates\payment
copy templates\fix_payment_select_school.html templates\payment\fix_payment_select_school.html
echo.

echo [3/5] Copie des fichiers vers production...
copy fix_payment_select_school.py production_code\ClassesNumerique-Secondaire-main\
copy diagnose_select_school_route.py production_code\ClassesNumerique-Secondaire-main\
copy integrate_select_school_fix.py production_code\ClassesNumerique-Secondaire-main\
copy integrate_app_select_school_fix.py production_code\ClassesNumerique-Secondaire-main\
copy templates\fix_payment_select_school.html production_code\ClassesNumerique-Secondaire-main\templates\payment\
echo.

echo [4/5] Integration de la correction...
python integrate_app_select_school_fix.py production_code\ClassesNumerique-Secondaire-main\app.py
echo.

echo [5/5] Preparation du commit Git...
git add fix_payment_select_school.py diagnose_select_school_route.py integrate_select_school_fix.py
git add integrate_app_select_school_fix.py templates\fix_payment_select_school.html
git add templates\payment\fix_payment_select_school.html
git add production_code\ClassesNumerique-Secondaire-main\fix_payment_select_school.py
git add production_code\ClassesNumerique-Secondaire-main\diagnose_select_school_route.py
git add production_code\ClassesNumerique-Secondaire-main\integrate_select_school_fix.py
git add production_code\ClassesNumerique-Secondaire-main\integrate_app_select_school_fix.py
git add production_code\ClassesNumerique-Secondaire-main\templates\payment\fix_payment_select_school.html
git add production_code\ClassesNumerique-Secondaire-main\app.py
git add DOCUMENTATION_CORRECTION_SELECT_SCHOOL_ROUTE.md
git add test_select_school_fix.py
echo.

echo ===================================================
echo Preparation terminee avec succes!
echo ===================================================
echo.
echo Pour finaliser le deploiement:
echo 1. Executez: git commit -m "Fix: Correction de l'erreur 500 sur la route /payment/select-school"
echo 2. Executez: git push
echo 3. Verifiez le deploiement sur Railway
echo.
echo Appuyez sur une touche pour quitter...
pause > nul
