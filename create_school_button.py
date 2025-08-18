"""
Script pour ajouter un bouton "Créer une école" dans la barre de navigation
et simplifier le processus d'inscription des écoles.
"""

from flask import Blueprint, redirect, url_for, render_template, flash, request
import os
import sys

# Créer un blueprint pour la fonctionnalité
school_registration_bp = Blueprint('school_registration', __name__, url_prefix='/school')

@school_registration_bp.route('/register', methods=['GET', 'POST'])
def register_school_simplified():
    """Route simplifiée pour l'inscription des écoles"""
    if request.method == 'POST':
        # Rediriger vers la route d'inscription existante
        return redirect(url_for('register_school'), code=307)  # 307 pour préserver la méthode POST
    
    # Afficher le formulaire simplifié
    return render_template('auth/register_school_simplified.html')

def register_blueprint(app):
    """Enregistre le blueprint dans l'application Flask"""
    app.register_blueprint(school_registration_bp)
    
    # Modifier la route existante pour rediriger vers la nouvelle interface si nécessaire
    @app.route('/register/school_simplified')
    def redirect_to_simplified_school_registration():
        return redirect(url_for('school_registration.register_school_simplified'))
    
    # Ajouter une route dans la barre de navigation
    @app.context_processor
    def inject_school_registration_url():
        return {
            'school_registration_url': url_for('school_registration.register_school_simplified')
        }
    
    app.logger.info("Blueprint d'inscription d'école simplifié enregistré avec succès")
    return True

def integrate_with_app():
    """Intègre le blueprint avec l'application principale"""
    try:
        # Ajouter le chemin du projet au PYTHONPATH
        sys.path.append(os.path.abspath('production_code/ClassesNumerique-Secondaire-main'))
        
        # Importer l'application Flask
        from app import app
        
        # Enregistrer le blueprint
        with app.app_context():
            register_blueprint(app)
        
        print("[SUCCÈS] Blueprint d'inscription d'école simplifié intégré avec succès")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec de l'intégration: {str(e)}")
        return False

if __name__ == "__main__":
    integrate_with_app()
