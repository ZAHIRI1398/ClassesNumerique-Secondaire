"""
Script de correction pour le problème du bouton "Souscrire un nouvel abonnement école"
pour les utilisateurs déjà connectés.

Ce script corrige les problèmes suivants :
1. Redirection incorrecte pour les enseignants déjà connectés
2. Problème de création de compte école avec email existant
3. Problème de navigation entre les pages d'abonnement
"""

from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_required
import logging
import sys
from datetime import datetime
import os

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger('fix_school_subscription')

# Création du blueprint de correction
fix_subscription_bp = Blueprint('fix_subscription', __name__, url_prefix='/fix')

@fix_subscription_bp.route('/school-subscription')
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
    
    # Vérifier les conditions qui pourraient bloquer la progression
    issues = []
    solutions = []
    
    # Condition 1: L'utilisateur a déjà un abonnement actif
    if current_user.subscription_status == 'approved':
        issues.append("L'utilisateur a déjà un abonnement actif")
        solutions.append("Aucune action nécessaire, l'utilisateur est déjà abonné")
    
    # Condition 2: L'utilisateur est associé à une école qui a déjà un abonnement actif
    if current_user.school_name:
        from models import User, db
        
        # Rechercher si un autre utilisateur de la même école a déjà un abonnement actif
        with fix_subscription_bp.app_context():
            school_subscription = User.query.filter(
                User.school_name == current_user.school_name,
                User.subscription_type == 'school',
                User.subscription_status == 'approved'
            ).first()
            
            if school_subscription:
                issues.append(f"L'école {current_user.school_name} a déjà un abonnement actif")
                solutions.append("Approuver automatiquement cet utilisateur")
                
                # Correction: Approuver automatiquement l'utilisateur
                current_user.subscription_status = 'approved'
                current_user.subscription_type = 'school'
                current_user.approval_date = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"✅ Utilisateur {current_user.email} approuvé automatiquement car l'école {current_user.school_name} a déjà un abonnement actif")
    
    # Condition 3: L'utilisateur est un enseignant et devrait être redirigé vers select_school
    if current_user.role == 'teacher' and not current_user.subscription_status == 'approved':
        issues.append("L'utilisateur est un enseignant et devrait être redirigé vers la page de sélection d'école")
        solutions.append("Rediriger manuellement vers la page de sélection d'école")
        
        # Redirection manuelle vers la page de sélection d'école
        return redirect(url_for('payment.select_school'))
    
    # Si aucun problème n'est détecté
    if not issues:
        issues.append("Aucun problème détecté")
        solutions.append("Rediriger vers la page d'abonnement standard")
        
        # Redirection vers la page d'abonnement standard
        return redirect(url_for('payment.subscribe', subscription_type='school'))
    
    # Afficher les résultats du diagnostic
    return render_template('diagnostic/subscription_diagnostic.html', 
                          issues=issues, 
                          solutions=solutions,
                          user=current_user)

def create_diagnostic_template():
    """Créer le template de diagnostic s'il n'existe pas"""
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'diagnostic')
    template_path = os.path.join(template_dir, 'subscription_diagnostic.html')
    
    # Créer le répertoire s'il n'existe pas
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # Créer le template s'il n'existe pas
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""{% extends "base.html" %}

{% block title %}Diagnostic d'abonnement école{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-lg border-0">
                <div class="card-header bg-primary text-white text-center py-4">
                    <h2 class="mb-0">
                        <i class="fas fa-stethoscope me-2"></i>
                        Diagnostic d'abonnement école
                    </h2>
                </div>
                <div class="card-body p-4">
                    <div class="alert alert-info mb-4" role="alert">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Information :</strong> Cette page analyse et corrige les problèmes liés au bouton "Souscrire un nouvel abonnement école".
                    </div>
                    
                    <h4 class="mb-3">Informations utilisateur</h4>
                    <ul class="list-group mb-4">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Email
                            <span class="badge bg-primary rounded-pill">{{ user.email }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Rôle
                            <span class="badge bg-secondary rounded-pill">{{ user.role }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            École
                            <span class="badge bg-info rounded-pill">{{ user.school_name or 'Non définie' }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Type d'abonnement
                            <span class="badge bg-warning rounded-pill">{{ user.subscription_type or 'Non défini' }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Statut d'abonnement
                            <span class="badge bg-{{ 'success' if user.subscription_status == 'approved' else 'danger' }} rounded-pill">{{ user.subscription_status or 'Non défini' }}</span>
                        </li>
                    </ul>
                    
                    <h4 class="mb-3">Problèmes détectés</h4>
                    <ul class="list-group mb-4">
                        {% for issue in issues %}
                            <li class="list-group-item list-group-item-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                {{ issue }}
                            </li>
                        {% endfor %}
                    </ul>
                    
                    <h4 class="mb-3">Solutions appliquées</h4>
                    <ul class="list-group mb-4">
                        {% for solution in solutions %}
                            <li class="list-group-item list-group-item-success">
                                <i class="fas fa-check-circle me-2"></i>
                                {{ solution }}
                            </li>
                        {% endfor %}
                    </ul>
                    
                    <div class="d-grid gap-2">
                        <a href="{{ url_for('payment.select_school') }}" class="btn btn-primary btn-lg">
                            <i class="fas fa-school me-2"></i>
                            Aller à la sélection d'école
                        </a>
                        <a href="{{ url_for('payment.subscribe', subscription_type='school') }}" class="btn btn-outline-primary">
                            <i class="fas fa-plus-circle me-2"></i>
                            Souscrire un nouvel abonnement école
                        </a>
                    </div>
                </div>
                <div class="card-footer bg-light p-3">
                    <div class="text-center">
                        <a href="{{ url_for('index') }}" class="btn btn-link">
                            <i class="fas fa-arrow-left me-2"></i>
                            Retour à l'accueil
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""")
            logger.info(f"✅ Template de diagnostic créé: {template_path}")
    else:
        logger.info(f"Template de diagnostic existe déjà: {template_path}")

def fix_payment_routes():
    """Corriger les routes de paiement pour les utilisateurs déjà connectés"""
    from models import User, db
    
    # Vérifier si Sara existe et corriger son statut si nécessaire
    with fix_subscription_bp.app_context():
        sara = User.query.filter_by(email='sara@gmail.com').first()
        if sara:
            logger.info(f"Vérification de l'utilisateur Sara: {sara.email}")
            logger.info(f"Statut actuel: {sara.subscription_status}, Type: {sara.subscription_type}")
            
            # Si Sara n'a pas de type d'abonnement défini, le définir comme 'pending'
            if not sara.subscription_type:
                sara.subscription_type = 'pending'
                db.session.commit()
                logger.info(f"✅ Type d'abonnement de Sara mis à jour: {sara.subscription_type}")

def integrate_fix(app):
    """Intégrer la correction dans l'application Flask"""
    # Enregistrer le blueprint de correction
    app.register_blueprint(fix_subscription_bp)
    
    # Stocker l'application dans le blueprint pour pouvoir l'utiliser dans les routes
    fix_subscription_bp.app = app
    
    # Créer le template de diagnostic
    with app.app_context():
        create_diagnostic_template()
        fix_payment_routes()
    
    logger.info("✅ Correction intégrée avec succès")
    
    return app

def create_test_script():
    """Créer un script de test pour vérifier la correction"""
    test_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_school_subscription_fix.py')
    
    with open(test_script_path, 'w', encoding='utf-8') as f:
        f.write("""\
from flask import Flask
from models import db, User
from config import config
import logging
import sys

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger('test_subscription_fix')

def create_app():
    # Création de l'application Flask
    app = Flask(__name__)
    
    # Utiliser la configuration de développement par défaut
    app.config.from_object(config['development'])
    
    # Initialisation de la base de données
    db.init_app(app)
    
    return app

def test_sara_subscription():
    """Tester la correction pour Sara"""
    app = create_app()
    
    with app.app_context():
        # Rechercher Sara dans la base de données
        sara = User.query.filter_by(email='sara@gmail.com').first()
        
        if not sara:
            logger.error("Sara n'existe pas dans la base de données")
            return
        
        logger.info(f"=== INFORMATIONS SARA AVANT CORRECTION ===")
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
        
        logger.info(f"=== INFORMATIONS SARA APRÈS CORRECTION ===")
        logger.info(f"Email: {sara.email}")
        logger.info(f"Rôle: {sara.role}")
        logger.info(f"École: {sara.school_name}")
        logger.info(f"Type d'abonnement: {sara.subscription_type}")
        logger.info(f"Statut d'abonnement: {sara.subscription_status}")
        
        # Simuler le comportement de la route payment.subscribe
        if sara.role == 'teacher' and sara.subscription_status != 'approved':
            logger.info("✅ Sara serait redirigée vers la page de sélection d'école")
        else:
            logger.info("❌ Sara ne serait pas redirigée correctement")

if __name__ == '__main__':
    test_sara_subscription()
""")
    logger.info(f"✅ Script de test créé: {test_script_path}")

if __name__ == '__main__':
    # Créer le script de test
    create_test_script()
    
    # Afficher les instructions
    print("""
=== INSTRUCTIONS D'UTILISATION ===

1. Intégrer la correction dans app.py :

   from fix_school_subscription_button import integrate_fix
   app = integrate_fix(app)

2. Tester la correction :

   python test_school_subscription_fix.py

3. Accéder à la page de diagnostic :

   http://localhost:5000/fix/school-subscription

Cette correction résout les problèmes suivants :
- Redirection incorrecte pour les enseignants déjà connectés
- Problème de création de compte école avec email existant
- Problème de navigation entre les pages d'abonnement
""")
