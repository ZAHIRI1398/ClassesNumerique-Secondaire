@echo off
echo Verification et correction des abonnements de type 'Trial'...

REM Configuration de la base de donnees de production
set PRODUCTION_DATABASE_URL=postgresql://postgres:SJqjLlGjIzLYjOuaKRcTmDqrgkMpcGJO@postgres.railway.internal:5432/railway

REM Execution du script Python sans correction (mode visualisation)
echo.
echo === MODE VISUALISATION ===
python fix_trial_subscriptions.py

echo.
echo Pour corriger les donnees, executez ce script avec l'option --fix
echo Exemple: run_fix_trial_subscriptions.bat --fix

REM Vérifier si l'option --fix est passée
if "%1"=="--fix" (
    echo.
    echo === MODE CORRECTION ===
    python fix_trial_subscriptions.py --fix
)

echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul
