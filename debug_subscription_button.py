from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, current_user, login_required
import logging
import sys
from datetime import datetime
import os
from models import db, User
from config import config

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger('debug_subscription')

# Création de l'application Flask
app = Flask(__name__)

# Utiliser la configuration de développement par défaut
app.config.from_object(config['development'])

# Initialisation de la base de données
db.init_app(app)

# Initialisation de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Fonction de chargement de l'utilisateur pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route de test pour simuler le clic sur le bouton d'abonnement école
@app.route('/test-subscribe-school')
@login_required
def test_subscribe_school():
    logger.info(f"=== TEST DU BOUTON D'ABONNEMENT ÉCOLE POUR {current_user.email} ===")
    
    # Afficher les informations de l'utilisateur connecté
    logger.info(f"Utilisateur: {current_user.email}")
    logger.info(f"Rôle: {current_user.role}")
    logger.info(f"École: {current_user.school_name}")
    logger.info(f"Type d'abonnement: {current_user.subscription_type}")
    logger.info(f"Statut d'abonnement: {current_user.subscription_status}")
    
    # Vérifier les conditions de redirection dans la route payment.subscribe
    if current_user.subscription_status == 'approved':
        logger.warning("Condition 1: L'utilisateur a déjà un abonnement actif")
        logger.warning("La route payment.subscribe redirigerait vers la page d'accueil")
        return "L'utilisateur a déjà un abonnement actif. La route redirigerait vers la page d'accueil."
    
    if current_user.school_name:
        # Rechercher si un autre utilisateur de la même école a déjà un abonnement actif
        school_subscription = User.query.filter(
            User.school_name == current_user.school_name,
            User.subscription_type == 'school',
            User.subscription_status == 'approved'
        ).first()
        
        if school_subscription:
            logger.warning(f"Condition 2: L'école {current_user.school_name} a déjà un abonnement actif")
            logger.warning("La route payment.subscribe approuverait automatiquement cet utilisateur")
            return f"L'école {current_user.school_name} a déjà un abonnement actif. L'utilisateur serait automatiquement approuvé."
    
    if current_user.role == 'teacher':
        logger.warning("Condition 3: L'utilisateur est un enseignant")
        logger.warning("La route payment.subscribe redirigerait vers payment.select_school")
        return "L'utilisateur est un enseignant. La route redirigerait vers la page de sélection d'école."
    
    # Si aucune condition de redirection n'est remplie
    logger.info("Aucune condition de redirection n'est remplie")
    logger.info("La route payment.subscribe afficherait la page de souscription")
    
    # Simuler l'URL qui serait générée pour le bouton
    subscription_url = url_for('payment.subscribe', subscription_type='school')
    logger.info(f"URL générée pour le bouton: {subscription_url}")
    
    # Vérifier si la route existe dans l'application
    try:
        from payment_routes import payment_bp
        logger.info("Le blueprint payment_bp est correctement importé")
        
        # Vérifier si la route subscribe existe dans le blueprint
        for rule in app.url_map.iter_rules():
            if 'payment.subscribe' in rule.endpoint:
                logger.info(f"Route trouvée: {rule}")
                logger.info(f"Méthodes: {rule.methods}")
                logger.info(f"Arguments: {rule.arguments}")
                break
        else:
            logger.error("La route payment.subscribe n'a pas été trouvée dans l'application")
    except ImportError:
        logger.error("Impossible d'importer le blueprint payment_bp")
    
    return f"Test terminé. URL générée pour le bouton: {subscription_url}"

# Route de test pour simuler le formulaire d'inscription d'école
@app.route('/test-register-school')
def test_register_school():
    logger.info("=== TEST DU FORMULAIRE D'INSCRIPTION D'ÉCOLE ===")
    
    # Vérifier si le template existe
    template_path = os.path.join('templates', 'auth', 'register_school_simplified.html')
    if os.path.exists(template_path):
        logger.info(f"Le template {template_path} existe")
    else:
        logger.error(f"Le template {template_path} n'existe pas")
    
    # Vérifier si le blueprint d'inscription d'école est importé
    try:
        from app import school_registration_mod
        logger.info("Le blueprint school_registration_mod est correctement importé dans app.py")
    except ImportError:
        logger.error("Impossible d'importer le blueprint school_registration_mod depuis app.py")
    
    return "Test du formulaire d'inscription d'école terminé"

# Route de test pour simuler la page de sélection d'école
@app.route('/test-select-school')
@login_required
def test_select_school():
    logger.info("=== TEST DE LA PAGE DE SÉLECTION D'ÉCOLE ===")
    
    # Vérifier si le template existe
    template_path = os.path.join('templates', 'payment', 'select_school.html')
    if os.path.exists(template_path):
        logger.info(f"Le template {template_path} existe")
    else:
        logger.error(f"Le template {template_path} n'existe pas")
    
    # Simuler la requête pour récupérer les écoles avec abonnement actif
    from sqlalchemy import func
    schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
        filter(User.school_name != None).\
        filter(User.school_name != '').\
        filter(User.subscription_type == 'school').\
        filter(User.subscription_status == 'approved').\
        group_by(User.school_name).all()
    
    logger.info(f"Écoles avec abonnement trouvées: {schools_with_subscription}")
    
    return f"Test de la page de sélection d'école terminé. {len(schools_with_subscription)} écoles trouvées."

# Route pour tester le bouton "Souscrire un nouvel abonnement école" directement
@app.route('/test-subscribe-button')
@login_required
def test_subscribe_button():
    logger.info("=== TEST DU BOUTON SOUSCRIRE UN NOUVEL ABONNEMENT ÉCOLE ===")
    
    # Simuler le clic sur le bouton
    try:
        subscription_url = '/payment/subscribe/school'
        logger.info(f"URL pour le bouton: {subscription_url}")
        
        # Analyser les conditions de redirection dans payment_routes.py
        logger.info("Analyse des conditions de redirection dans payment_routes.py:")
        
        # Condition 1: L'utilisateur a déjà un abonnement actif
        if current_user.subscription_status == 'approved':
            logger.warning("Condition 1: L'utilisateur a déjà un abonnement actif")
            logger.warning("La route payment.subscribe redirigerait vers la page d'accueil")
            return "L'utilisateur a déjà un abonnement actif. La route redirigerait vers la page d'accueil."
        
        # Condition 2: L'utilisateur est associé à une école qui a déjà un abonnement actif
        if current_user.school_name:
            # Rechercher si un autre utilisateur de la même école a déjà un abonnement actif
            school_subscription = User.query.filter(
                User.school_name == current_user.school_name,
                User.subscription_type == 'school',
                User.subscription_status == 'approved'
            ).first()
            
            if school_subscription:
                logger.warning(f"Condition 2: L'école {current_user.school_name} a déjà un abonnement actif")
                logger.warning("La route payment.subscribe approuverait automatiquement cet utilisateur")
                return f"L'école {current_user.school_name} a déjà un abonnement actif. L'utilisateur serait automatiquement approuvé."
        
        # Condition 3: L'utilisateur est un enseignant et serait redirigé vers select_school
        if current_user.role == 'teacher':
            logger.warning("Condition 3: L'utilisateur est un enseignant")
            logger.warning("La route payment.subscribe redirigerait vers payment.select_school")
            return "L'utilisateur est un enseignant. La route redirigerait vers la page de sélection d'école."
        
        # Si aucune condition de redirection n'est remplie
        logger.info("Aucune condition de redirection n'est remplie")
        logger.info("La route payment.subscribe afficherait la page de souscription")
        
        return "Test du bouton terminé. La route afficherait la page de souscription."
    except Exception as e:
        logger.error(f"Erreur lors du test: {str(e)}")
        return f"Erreur lors du test: {str(e)}"

# Route pour tester la connexion à la base de données
@app.route('/test-db')
def test_db():
    logger.info("=== TEST DE LA CONNEXION À LA BASE DE DONNÉES ===")
    
    try:
        # Vérifier que la connexion à la base de données fonctionne
        user_count = User.query.count()
        logger.info(f"Nombre d'utilisateurs dans la base de données: {user_count}")
        
        # Récupérer quelques utilisateurs pour vérifier
        users = User.query.limit(5).all()
        for user in users:
            logger.info(f"Utilisateur: {user.email}, Rôle: {user.role}, École: {user.school_name}")
        
        return f"Test de la base de données terminé. {user_count} utilisateurs trouvés."
    except Exception as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {str(e)}")
        return f"Erreur lors du test: {str(e)}"

# Route pour tester la connexion d'un utilisateur spécifique
@app.route('/test-login/<email>')
def test_login(email):
    logger.info(f"=== TEST DE CONNEXION POUR {email} ===")
    
    try:
        # Rechercher l'utilisateur dans la base de données
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.error(f"Utilisateur {email} non trouvé dans la base de données")
            return f"Utilisateur {email} non trouvé"
        
        # Connecter l'utilisateur
        login_user(user)
        logger.info(f"Utilisateur {email} connecté avec succès")
        logger.info(f"Rôle: {user.role}, École: {user.school_name}")
        logger.info(f"Type d'abonnement: {user.subscription_type}, Statut: {user.subscription_status}")
        
        return f"Utilisateur {email} connecté avec succès"
    except Exception as e:
        logger.error(f"Erreur lors de la connexion de l'utilisateur: {str(e)}")
        return f"Erreur lors du test: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        # Afficher les informations de configuration
        logger.info("=== CONFIGURATION DE L'APPLICATION ===")
        logger.info(f"Mode debug: {app.debug}")
        logger.info(f"Base de données: {app.config['SQLALCHEMY_DATABASE_URI']}")
        logger.info(f"Secret key: {'Définie' if app.config['SECRET_KEY'] else 'Non définie'}")
        
        # Vérifier les blueprints enregistrés
        logger.info("=== BLUEPRINTS ENREGISTRÉS ===")
        for blueprint in app.blueprints:
            logger.info(f"Blueprint: {blueprint}, URL prefix: {app.blueprints[blueprint].url_prefix}")
        
        # Vérifier les routes enregistrées
        logger.info("=== ROUTES ENREGISTRÉES ===")
        for rule in app.url_map.iter_rules():
            logger.info(f"Route: {rule}, Endpoint: {rule.endpoint}, Méthodes: {rule.methods}")
    
    # Démarrer l'application en mode debug
    app.run(debug=True, port=5001)
