
from flask import Blueprint, redirect, url_for, flash, current_app
from flask_login import current_user, login_required

def integrate_school_payment(app):
    """
    Intègre le module de paiement d'école à l'application Flask.
    Cette fonction crée un blueprint pour gérer les redirections entre
    l'inscription d'école et le système de paiement.
    """
    # Création du blueprint
    school_payment_bp = Blueprint('school_payment', __name__)
    
    @school_payment_bp.route('/register-school-to-payment')
    @login_required
    def register_school_to_payment():
        """
        Route de redirection après la création d'une école pour initier le processus de paiement.
        """
        # Vérifier si l'utilisateur est associé à une école
        if not current_user.school_id:
            flash('Vous devez d\'abord créer une école avant de procéder au paiement.', 'warning')
            return redirect(url_for('school_registration_mod.register_school_simplified'))
        
        # Rediriger vers la page de paiement pour un abonnement école
        return redirect(url_for('payment.subscribe', subscription_type='school'))
    
    # Enregistrer le blueprint dans l'application
    app.register_blueprint(school_payment_bp)
    
    # Modifier les routes d'inscription d'école pour rediriger vers le paiement
    try:
        # Récupérer le blueprint d'inscription d'école directement depuis l'application
        school_registration_mod = app.blueprints.get('school_registration_mod')
        
        if not school_registration_mod:
            app.logger.warning("Le blueprint d'inscription d'école n'a pas été trouvé dans l'application.")
            return app
            
        # Sauvegarder les fonctions originales
        original_register_school_simplified = school_registration_mod.view_functions.get('register_school_simplified')
        original_register_school_connected = school_registration_mod.view_functions.get('register_school_connected')
        
        if original_register_school_simplified and original_register_school_connected:
            # Définir les nouvelles fonctions avec redirection vers le paiement
            @school_registration_mod.route('/register-school-simplified', methods=['GET', 'POST'])
            @login_required
            def register_school_simplified_with_payment():
                # Appeler la fonction originale
                result = original_register_school_simplified()
                
                # Si c'est une redirection (après création réussie), rediriger vers le paiement
                if hasattr(result, 'status_code') and result.status_code == 302:
                    app.logger.info("École créée avec succès, redirection vers le paiement...")
                    return redirect(url_for('school_payment.register_school_to_payment'))
                
                # Sinon, retourner le résultat original
                return result
            
            @school_registration_mod.route('/register-school-connected', methods=['GET', 'POST'])
            @login_required
            def register_school_connected_with_payment():
                # Appeler la fonction originale
                result = original_register_school_connected()
                
                # Si c'est une redirection (après création réussie), rediriger vers le paiement
                if hasattr(result, 'status_code') and result.status_code == 302:
                    app.logger.info("École créée avec succès, redirection vers le paiement...")
                    return redirect(url_for('school_payment.register_school_to_payment'))
                
                # Sinon, retourner le résultat original
                return result
            
            # Remplacer les fonctions originales par les nouvelles
            school_registration_mod.view_functions['register_school_simplified'] = register_school_simplified_with_payment
            school_registration_mod.view_functions['register_school_connected'] = register_school_connected_with_payment
            
            app.logger.info("Intégration du module de paiement d'école terminée.")
        else:
            app.logger.warning("Les fonctions d'inscription d'école n'ont pas été trouvées. L'intégration n'a pas pu être effectuée.")
    
    except ImportError:
        app.logger.warning("Le module d'inscription d'école n'a pas été trouvé. L'intégration n'a pas pu être effectuée.")
    
    return app
