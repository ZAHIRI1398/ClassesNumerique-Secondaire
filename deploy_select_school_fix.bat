@echo off
echo ===================================================
echo Deploiement de la correction pour select-school
echo ===================================================
echo.

echo [1/6] Verification des fichiers...
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
echo Tous les fichiers necessaires sont presents.
echo.

echo [2/6] Creation d'une sauvegarde...
if not exist backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%\ (
    mkdir backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%
)
if exist app.py (
    copy app.py backup_select_school_fix_%date:~6,4%%date:~3,2%%date:~0,2%\app.py.bak
    echo Sauvegarde de app.py creee.
)
echo.

echo [3/6] Preparation des fichiers pour le commit...
echo Copie des fichiers vers le repertoire templates...
if not exist templates\payment\ (
    mkdir templates\payment
)
copy templates\fix_payment_select_school.html templates\payment\fix_payment_select_school.html
echo.

echo [4/6] Ajout des fichiers au commit Git...
git add fix_payment_select_school.py
git add diagnose_select_school_route.py
git add integrate_select_school_fix.py
git add templates\fix_payment_select_school.html
git add templates\payment\fix_payment_select_school.html
echo.

echo [5/6] Creation du commit...
git commit -m "Fix: Correction de l'erreur 500 sur la route /payment/select-school"
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de creer le commit Git.
    exit /b 1
)
echo.

echo [6/6] Push vers le depot distant...
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
echo Pour activer la correction en production:
echo 1. Connectez-vous a l'interface d'administration Railway
echo 2. Verifiez que le deploiement s'est termine avec succes
echo 3. Accedez a l'URL: https://votre-domaine.up.railway.app/diagnose/select-school-route
echo 4. Analysez les resultats du diagnostic
echo 5. Testez la version corrigee via: https://votre-domaine.up.railway.app/fix-payment/select-school
echo.
echo Appuyez sur une touche pour quitter...
pause > nul
