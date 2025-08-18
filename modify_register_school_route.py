"""
Script pour modifier la route d'inscription d'école afin de gérer les utilisateurs déjà connectés
"""

from flask import Blueprint, redirect, url_for, render_template, flash, request, current_app
from flask_login import current_user, login_required
import os
import sys

# Créer un blueprint pour la fonctionnalité
school_registration_mod_bp = Blueprint('school_registration_mod', __name__)

@school_registration_mod_bp.route('/register/school', methods=['GET', 'POST'])
def register_school_modified():
    """Route modifiée pour l'inscription des écoles qui gère les utilisateurs connectés"""
    # Si l'utilisateur est déjà connecté, on utilise son compte existant
    if current_user.is_authenticated:
        if request.method == 'POST':
            # Récupérer le nom de l'école
            school_name = request.form.get('school_name')
            
            try:
                # Importer les modèles nécessaires
                from models import User, db
                
                # Mettre à jour l'utilisateur existant
                current_user.school_name = school_name
                current_user.subscription_type = 'school'  # Définir le type d'abonnement comme école
                
                # Enregistrer les modifications
                db.session.commit()
                
                # Rediriger vers la page de paiement
                flash('Votre compte a été associé à l\'école avec succès. Vous pouvez maintenant souscrire un abonnement.', 'success')
                return redirect(url_for('subscription_choice'))
                
            except Exception as e:
                current_app.logger.error(f"Erreur lors de l'association de l'école: {str(e)}")
                flash('Une erreur est survenue lors de l\'association de votre compte à l\'école.', 'error')
                return redirect(url_for('school_registration_mod.register_school_modified'))
        
        # Afficher le formulaire pour utilisateur connecté
        return render_template('auth/register_school_connected.html')
    else:
        # Rediriger vers la route d'inscription standard pour les nouveaux utilisateurs
        if request.method == 'POST':
            return redirect(url_for('register_school'), code=307)  # 307 pour préserver la méthode POST
        return render_template('auth/register_school_connected.html')

def register_blueprint(app):
    """Enregistre le blueprint dans l'application Flask"""
    app.register_blueprint(school_registration_mod_bp)
    
    # Remplacer la route existante
    app.view_functions['register_school'] = school_registration_mod_bp.view_functions['register_school_modified']
    
    app.logger.info("Route d'inscription d'école modifiée enregistrée avec succès")
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
        
        print("[SUCCÈS] Route d'inscription d'école modifiée intégrée avec succès")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec de l'intégration: {str(e)}")
        return False

if __name__ == "__main__":
    integrate_with_app()
