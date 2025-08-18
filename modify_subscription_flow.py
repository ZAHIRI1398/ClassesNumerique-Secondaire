"""
Script pour modifier le flux d'abonnement afin d'intégrer la création d'école simplifiée
"""

from flask import Blueprint, redirect, url_for, render_template, flash, request, current_app
import os
import sys

# Créer un blueprint pour la fonctionnalité
subscription_flow_bp = Blueprint('subscription_flow', __name__, url_prefix='/subscription')

@subscription_flow_bp.route('/choice', methods=['GET'])
def subscription_choice_improved():
    """Route améliorée pour le choix du type d'abonnement"""
    return render_template('subscription/choice_improved.html')

def register_blueprint(app):
    """Enregistre le blueprint dans l'application Flask"""
    app.register_blueprint(subscription_flow_bp)
    
    # Rediriger l'ancienne route vers la nouvelle
    @app.route('/subscription/choice/improved')
    def redirect_to_improved_subscription_choice():
        return redirect(url_for('subscription_flow.subscription_choice_improved'))
    
    app.logger.info("Blueprint de flux d'abonnement amélioré enregistré avec succès")
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
        
        print("[SUCCÈS] Blueprint de flux d'abonnement amélioré intégré avec succès")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec de l'intégration: {str(e)}")
        return False

if __name__ == "__main__":
    integrate_with_app()
