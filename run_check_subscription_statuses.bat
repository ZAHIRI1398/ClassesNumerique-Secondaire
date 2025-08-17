@echo off
echo Verification des statuts d'abonnement des ecoles en production...

REM Configuration de la base de donnees de production
set PRODUCTION_DATABASE_URL=postgresql://postgres:SJqjLlGjIzLYjOuaKRcTmDqrgkMpcGJO@postgres.railway.internal:5432/railway

REM Execution du script Python
python check_subscription_statuses.py

echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul
