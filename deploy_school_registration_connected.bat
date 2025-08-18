@echo off
echo ===================================================
echo Déploiement de l'amélioration d'inscription d'école
echo ===================================================
echo.

REM Créer les répertoires nécessaires s'ils n'existent pas
if not exist "templates\auth" mkdir "templates\auth"

REM Copier les fichiers de template
echo Copie des templates...
copy /Y "templates\auth\register_school_connected.html" "production_code\ClassesNumerique-Secondaire-main\templates\auth\"

REM Copier les scripts Python
echo Copie des scripts Python...
copy /Y "modify_register_school_route.py" "production_code\ClassesNumerique-Secondaire-main\blueprints\school_registration_mod.py"

REM Créer un script d'intégration pour app.py
echo Création du script d'intégration...
echo from blueprints.school_registration_mod import register_blueprint > "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration_mod.py"
echo. >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration_mod.py"
echo def integrate_school_registration_mod(app): >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration_mod.py"
echo     """Intègre la modification de la route d'inscription d'école""" >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration_mod.py"
echo     register_blueprint(app) >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration_mod.py"
echo     app.logger.info("Route d'inscription d'école modifiée intégrée avec succès") >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration_mod.py"
echo     return True >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration_mod.py"

REM Créer un script de test pour vérifier l'intégration
echo Création du script de test...
echo import os > "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo import sys >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo from flask import url_for >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo from flask_login import current_user >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo. >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo def test_route(): >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo     """Teste si la route modifiée est correctement enregistrée""" >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo     from app import app >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo     with app.test_request_context(): >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo         try: >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo             # Vérifier si la route existe >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo             url = url_for('register_school') >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo             print(f"[SUCCÈS] Route d'inscription d'école modifiée enregistrée: {url}") >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo             return True >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo         except Exception as e: >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo             print(f"[ERREUR] La route n'est pas correctement enregistrée: {str(e)}") >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo             return False >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo. >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo if __name__ == "__main__": >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"
echo     test_route() >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration_mod.py"

echo.
echo Déploiement terminé. Pour activer les modifications:
echo 1. Ajoutez dans app.py:
echo    from integrate_school_registration_mod import integrate_school_registration_mod
echo    integrate_school_registration_mod(app)
echo 2. Testez avec python test_school_registration_mod.py
echo 3. Commitez et pushez les changements vers GitHub
echo 4. Déployez sur Railway
echo.
echo Appuyez sur une touche pour terminer...
pause > nul
