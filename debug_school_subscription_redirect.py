from flask import Flask, request, redirect, url_for, flash
from flask_login import current_user
import logging
import sys
from models import db, User
from config import config
import os

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger('debug_subscription')

def create_app():
    # Création de l'application Flask
    app = Flask(__name__)
    
    # Utiliser la configuration de développement par défaut
    app.config.from_object(config['development'])
    
    # Initialisation de la base de données
    db.init_app(app)
    
    return app

def check_user_subscription(email):
    """Vérifier les informations d'abonnement d'un utilisateur"""
    app = create_app()
    
    with app.app_context():
        # Rechercher l'utilisateur dans la base de données
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.error(f"Utilisateur {email} non trouvé dans la base de données")
            return None
        
        logger.info(f"=== INFORMATIONS UTILISATEUR {email} ===")
        logger.info(f"Rôle: {user.role}")
        logger.info(f"École: {user.school_name}")
        logger.info(f"Type d'abonnement: {user.subscription_type}")
        logger.info(f"Statut d'abonnement: {user.subscription_status}")
        
        # Analyser les conditions de redirection dans payment_routes.py
        logger.info("=== ANALYSE DES CONDITIONS DE REDIRECTION ===")
        
        # Condition 1: L'utilisateur a déjà un abonnement actif
        if user.subscription_status == 'approved':
            logger.warning("Condition 1: L'utilisateur a déjà un abonnement actif")
            logger.warning("La route payment.subscribe redirigerait vers la page d'accueil")
            return "L'utilisateur a déjà un abonnement actif. La route redirigerait vers la page d'accueil."
        
        # Condition 2: L'utilisateur est associé à une école qui a déjà un abonnement actif
        if user.school_name:
            # Rechercher si un autre utilisateur de la même école a déjà un abonnement actif
            school_subscription = User.query.filter(
                User.school_name == user.school_name,
                User.subscription_type == 'school',
                User.subscription_status == 'approved'
            ).first()
            
            if school_subscription:
                logger.warning(f"Condition 2: L'école {user.school_name} a déjà un abonnement actif")
                logger.warning("La route payment.subscribe approuverait automatiquement cet utilisateur")
                return f"L'école {user.school_name} a déjà un abonnement actif. L'utilisateur serait automatiquement approuvé."
        
        # Condition 3: L'utilisateur est un enseignant et serait redirigé vers select_school
        if user.role == 'teacher':
            logger.warning("Condition 3: L'utilisateur est un enseignant")
            logger.warning("La route payment.subscribe redirigerait vers payment.select_school")
            return "L'utilisateur est un enseignant. La route redirigerait vers la page de sélection d'école."
        
        # Si aucune condition de redirection n'est remplie
        logger.info("Aucune condition de redirection n'est remplie")
        logger.info("La route payment.subscribe afficherait la page de souscription")
        
        return "La route afficherait la page de souscription."

def check_school_subscriptions():
    """Vérifier toutes les écoles avec abonnement actif"""
    app = create_app()
    
    with app.app_context():
        logger.info("=== VÉRIFICATION DES ÉCOLES AVEC ABONNEMENT ACTIF ===")
        
        # Récupérer toutes les écoles distinctes
        all_schools = db.session.query(User.school_name).filter(
            User.school_name != None,
            User.school_name != ''
        ).distinct().all()
        
        logger.info(f"Nombre total d'écoles: {len(all_schools)}")
        
        for school in all_schools:
            school_name = school.school_name
            logger.info(f"=== ÉCOLE: {school_name} ===")
            
            # Vérifier les utilisateurs de cette école
            school_users = User.query.filter_by(school_name=school_name).all()
            logger.info(f"Nombre d'utilisateurs: {len(school_users)}")
            
            # Vérifier si l'école a un abonnement actif
            school_subscription = User.query.filter(
                User.school_name == school_name,
                User.subscription_type == 'school',
                User.subscription_status == 'approved'
            ).first()
            
            if school_subscription:
                logger.info(f"✅ L'école a un abonnement actif (utilisateur: {school_subscription.email})")
            else:
                logger.warning(f"❌ L'école n'a pas d'abonnement actif")
                
                # Vérifier s'il y a des utilisateurs avec un abonnement école mais un statut différent
                other_status = User.query.filter(
                    User.school_name == school_name,
                    User.subscription_type == 'school',
                    User.subscription_status != 'approved'
                ).all()
                
                if other_status:
                    for user in other_status:
                        logger.warning(f"Utilisateur avec abonnement école mais statut non approuvé: {user.email}, Statut: {user.subscription_status}")

def fix_user_subscription(email, new_status=None, new_type=None):
    """Corriger les informations d'abonnement d'un utilisateur"""
    app = create_app()
    
    with app.app_context():
        # Rechercher l'utilisateur dans la base de données
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.error(f"Utilisateur {email} non trouvé dans la base de données")
            return False
        
        logger.info(f"=== CORRECTION UTILISATEUR {email} ===")
        logger.info(f"Avant: Type={user.subscription_type}, Statut={user.subscription_status}")
        
        # Mettre à jour le statut d'abonnement si spécifié
        if new_status:
            user.subscription_status = new_status
        
        # Mettre à jour le type d'abonnement si spécifié
        if new_type:
            user.subscription_type = new_type
        
        # Enregistrer les modifications
        db.session.commit()
        
        logger.info(f"Après: Type={user.subscription_type}, Statut={user.subscription_status}")
        return True

if __name__ == '__main__':
    # Vérifier les arguments de ligne de commande
    import argparse
    
    parser = argparse.ArgumentParser(description='Déboguer les problèmes d\'abonnement école')
    parser.add_argument('--check-user', type=str, help='Vérifier les informations d\'abonnement d\'un utilisateur')
    parser.add_argument('--check-schools', action='store_true', help='Vérifier toutes les écoles avec abonnement actif')
    parser.add_argument('--fix-user', type=str, help='Corriger les informations d\'abonnement d\'un utilisateur')
    parser.add_argument('--new-status', type=str, help='Nouveau statut d\'abonnement')
    parser.add_argument('--new-type', type=str, help='Nouveau type d\'abonnement')
    
    args = parser.parse_args()
    
    if args.check_user:
        check_user_subscription(args.check_user)
    elif args.check_schools:
        check_school_subscriptions()
    elif args.fix_user:
        if not args.new_status and not args.new_type:
            logger.error("Veuillez spécifier au moins un nouveau statut ou type d'abonnement")
        else:
            fix_user_subscription(args.fix_user, args.new_status, args.new_type)
    else:
        # Par défaut, vérifier l'utilisateur "sara@example.com"
        check_user_subscription("sara@example.com")
