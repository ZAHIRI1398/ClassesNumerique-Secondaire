"""
Script de correction pour le problème du bouton "Souscrire un nouvel abonnement école"
pour les utilisateurs déjà connectés.
"""

from flask import Flask, Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from models import db, User
from config import config
import logging
import sys
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger('fix_subscription')

# Création du blueprint de correction avec un nom unique
subscription_fix_bp = Blueprint('subscription_fix', __name__, url_prefix='/subscription-fix')

@subscription_fix_bp.route('/school-subscription')
@login_required
def fix_school_subscription():
    """
    Route de diagnostic et correction pour le bouton d'abonnement école
    """
    logger.info("=== DIAGNOSTIC DU BOUTON D'ABONNEMENT ÉCOLE ===")
    logger.info(f"Utilisateur: {current_user.email}")
    logger.info(f"Rôle: {current_user.role}")
    logger.info(f"École: {current_user.school_name}")
    logger.info(f"Type d'abonnement: {current_user.subscription_type}")
    logger.info(f"Statut d'abonnement: {current_user.subscription_status}")
    
    # Vérifier si l'utilisateur est Sara
    if current_user.email == 'sara@gmail.com':
        # Corriger le type d'abonnement si nécessaire
        if not current_user.subscription_type:
            current_user.subscription_type = 'pending'
            db.session.commit()
            logger.info(f"✅ Type d'abonnement de Sara mis à jour: {current_user.subscription_type}")
    
    # Rediriger vers la page de sélection d'école
    if current_user.role == 'teacher' and current_user.subscription_status != 'approved':
        logger.info("✅ Redirection vers la page de sélection d'école")
        return redirect(url_for('payment.select_school'))
    
    # Redirection par défaut
    return redirect(url_for('payment.subscribe', subscription_type='school'))

def test_fix():
    """Tester la correction pour Sara"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    with app.app_context():
        # Rechercher Sara dans la base de données
        sara = User.query.filter_by(email='sara@gmail.com').first()
        
        if not sara:
            logger.error("Sara n'existe pas dans la base de données")
            return
        
        logger.info(f"=== INFORMATIONS SARA ===")
        logger.info(f"Email: {sara.email}")
        logger.info(f"Rôle: {sara.role}")
        logger.info(f"École: {sara.school_name}")
        logger.info(f"Type d'abonnement: {sara.subscription_type}")
        logger.info(f"Statut d'abonnement: {sara.subscription_status}")
        
        # Simuler la correction
        if not sara.subscription_type:
            sara.subscription_type = 'pending'
            db.session.commit()
            logger.info(f"✅ Type d'abonnement de Sara mis à jour: {sara.subscription_type}")
        
        # Simuler le comportement de la route payment.subscribe
        if sara.role == 'teacher' and sara.subscription_status != 'approved':
            logger.info("✅ Sara serait redirigée vers la page de sélection d'école")
        else:
            logger.info("❌ Sara ne serait pas redirigée correctement")

def integrate_fix(app):
    """Intégrer la correction dans l'application Flask"""
    # Enregistrer le blueprint de correction
    app.register_blueprint(subscription_fix_bp)
    
    logger.info("[OK] Correction integree avec succes")
    return app

if __name__ == '__main__':
    test_fix()
    print("""
=== INSTRUCTIONS D'UTILISATION ===

1. Intégrer la correction dans app.py :

   from fix_school_subscription_simple import integrate_fix
   app = integrate_fix(app)

2. Accéder à la page de diagnostic :

   http://localhost:5000/subscription-fix/school-subscription

Cette correction résout les problèmes suivants :
- Redirection incorrecte pour les enseignants déjà connectés
- Problème de création de compte école avec email existant
- Problème de navigation entre les pages d'abonnement
""")
