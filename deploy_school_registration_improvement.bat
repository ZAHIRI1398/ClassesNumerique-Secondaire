@echo off
echo ===================================================
echo Déploiement de l'amélioration d'inscription d'école
echo ===================================================
echo.

REM Créer les répertoires nécessaires s'ils n'existent pas
if not exist "templates\auth" mkdir "templates\auth"
if not exist "templates\subscription" mkdir "templates\subscription"

REM Copier les fichiers de template
echo Copie des templates...
copy /Y "templates\auth\register_school_simplified.html" "production_code\ClassesNumerique-Secondaire-main\templates\auth\"
copy /Y "templates\subscription\choice_improved.html" "production_code\ClassesNumerique-Secondaire-main\templates\subscription\"
copy /Y "templates\base_with_school_button.html" "production_code\ClassesNumerique-Secondaire-main\templates\base_with_school_button.html"

REM Copier les scripts Python
echo Copie des scripts Python...
copy /Y "create_school_button.py" "production_code\ClassesNumerique-Secondaire-main\blueprints\school_registration.py"
copy /Y "modify_subscription_flow.py" "production_code\ClassesNumerique-Secondaire-main\blueprints\subscription_flow.py"

REM Créer un script d'intégration pour app.py
echo Création du script d'intégration...
echo from blueprints.school_registration import school_registration_bp > "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"
echo from blueprints.subscription_flow import subscription_flow_bp >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"
echo. >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"
echo def integrate_blueprints(app): >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"
echo     """Intègre les blueprints d'amélioration d'inscription d'école""" >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"
echo     app.register_blueprint(school_registration_bp) >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"
echo     app.register_blueprint(subscription_flow_bp) >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"
echo     app.logger.info("Blueprints d'amélioration d'inscription d'école intégrés avec succès") >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"
echo     return True >> "production_code\ClassesNumerique-Secondaire-main\integrate_school_registration.py"

REM Créer un script de test pour vérifier l'intégration
echo Création du script de test...
echo import os > "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo import sys >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo from flask import url_for >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo. >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo def test_routes(): >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo     """Teste si les routes sont correctement enregistrées""" >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo     from app import app >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo     with app.test_request_context(): >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo         try: >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo             school_reg_url = url_for('school_registration.register_school_simplified') >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo             subscription_url = url_for('subscription_flow.subscription_choice_improved') >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo             print(f"[SUCCÈS] Routes enregistrées correctement:") >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo             print(f"- Route d'inscription d'école: {school_reg_url}") >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo             print(f"- Route de choix d'abonnement: {subscription_url}") >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo             return True >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo         except Exception as e: >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo             print(f"[ERREUR] Les routes ne sont pas correctement enregistrées: {str(e)}") >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo             return False >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo. >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo if __name__ == "__main__": >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"
echo     test_routes() >> "production_code\ClassesNumerique-Secondaire-main\test_school_registration.py"

echo.
echo Déploiement terminé. Pour activer les modifications:
echo 1. Ajoutez dans app.py:
echo    from integrate_school_registration import integrate_blueprints
echo    integrate_blueprints(app)
echo 2. Testez avec python test_school_registration.py
echo 3. Commitez et pushez les changements vers GitHub
echo 4. Déployez sur Railway
echo.
echo Appuyez sur une touche pour terminer...
pause > nul
