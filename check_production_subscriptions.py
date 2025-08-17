#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnostic pour vérifier les écoles et leurs abonnements en production
Ce script se connecte à la base de données PostgreSQL de production
"""

import os
import sys
import logging
import requests
from datetime import datetime
from flask import Flask
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"check_production_subscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("check_production_subscriptions")

# Création d'une application Flask minimale pour le contexte
app = Flask(__name__)

# Configuration de la base de données de production
# Remplacez cette URL par l'URL de votre base de données PostgreSQL de production
DATABASE_URL = os.environ.get('PRODUCTION_DATABASE_URL')
if not DATABASE_URL:
    logger.error("❌ La variable d'environnement PRODUCTION_DATABASE_URL n'est pas définie")
    logger.info("Pour exécuter ce script, définissez la variable d'environnement avec l'URL de la base de données PostgreSQL de production")
    logger.info("Exemple: set PRODUCTION_DATABASE_URL=postgresql://username:password@hostname:port/database_name")
    sys.exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Initialisation de la base de données
try:
    engine = create_engine(DATABASE_URL)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    Base = declarative_base()
    Base.query = db_session.query_property()
    logger.info("✅ Connexion à la base de données de production initialisée")
except Exception as e:
    logger.error(f"❌ Erreur lors de l'initialisation de la connexion à la base de données: {e}")
    sys.exit(1)

# Modèle User simplifié pour le diagnostic
class User(Base):
    __tablename__ = 'users'
    
    id = Base.metadata.tables['users'].c.id
    email = Base.metadata.tables['users'].c.email
    school_name = Base.metadata.tables['users'].c.school_name
    subscription_type = Base.metadata.tables['users'].c.subscription_type
    subscription_status = Base.metadata.tables['users'].c.subscription_status
    role = Base.metadata.tables['users'].c.role
    approval_date = Base.metadata.tables['users'].c.approval_date

def check_database_connection():
    """Vérifie la connexion à la base de données"""
    try:
        db_session.execute(text('SELECT 1'))
        logger.info("✅ Connexion à la base de données de production réussie")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def check_all_schools():
    """Affiche toutes les écoles dans la base de données"""
    try:
        schools = db_session.query(User.school_name).filter(
            User.school_name != None,
            User.school_name != ''
        ).distinct().all()
        
        logger.info(f"📚 Nombre total d'écoles dans la base: {len(schools)}")
        for idx, (school,) in enumerate(schools, 1):
            logger.info(f"  {idx}. {school}")
        return schools
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des écoles: {e}")
        return []

def check_schools_with_subscriptions():
    """Vérifie les écoles avec abonnements actifs"""
    try:
        # Requête pour trouver les écoles avec abonnement actif
        schools_with_subscription = db_session.query(
            User.school_name, 
            func.count(User.id).label('user_count')
        ).filter(
            User.school_name != None,
            User.school_name != '',
            User.subscription_type == 'school',
            User.subscription_status == 'approved'
        ).group_by(User.school_name).all()
        
        logger.info(f"🔍 Écoles avec abonnement actif: {len(schools_with_subscription)}")
        for idx, (school, count) in enumerate(schools_with_subscription, 1):
            logger.info(f"  {idx}. {school} - {count} utilisateurs")
        
        return schools_with_subscription
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des abonnements: {e}")
        return []

def check_subscription_details():
    """Affiche les détails des abonnements pour chaque école"""
    try:
        # Récupérer toutes les écoles
        schools = db_session.query(User.school_name).filter(
            User.school_name != None,
            User.school_name != ''
        ).distinct().all()
        
        logger.info("📊 Détails des abonnements par école:")
        for idx, (school_name,) in enumerate(schools, 1):
            # Compter les utilisateurs par type d'abonnement et statut
            subscription_stats = db_session.query(
                User.subscription_type,
                User.subscription_status,
                func.count(User.id).label('count')
            ).filter(
                User.school_name == school_name
            ).group_by(
                User.subscription_type,
                User.subscription_status
            ).all()
            
            logger.info(f"\n  École {idx}: {school_name}")
            for sub_type, status, count in subscription_stats:
                logger.info(f"    - Type: {sub_type or 'Non défini'}, Statut: {status or 'Non défini'}, Nombre: {count}")
            
            # Vérifier si l'école a un abonnement actif
            has_active = any(
                sub_type == 'school' and status == 'approved'
                for sub_type, status, _ in subscription_stats
            )
            
            if has_active:
                logger.info(f"    ✅ Cette école a un abonnement actif")
            else:
                logger.info(f"    ❌ Cette école n'a PAS d'abonnement actif")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des détails d'abonnement: {e}")
        return False

def check_user_roles_by_school():
    """Affiche la répartition des rôles par école"""
    try:
        # Récupérer toutes les écoles
        schools = db_session.query(User.school_name).filter(
            User.school_name != None,
            User.school_name != ''
        ).distinct().all()
        
        logger.info("👥 Répartition des rôles par école:")
        for idx, (school_name,) in enumerate(schools, 1):
            # Compter les utilisateurs par rôle
            role_stats = db_session.query(
                User.role,
                func.count(User.id).label('count')
            ).filter(
                User.school_name == school_name
            ).group_by(
                User.role
            ).all()
            
            logger.info(f"\n  École {idx}: {school_name}")
            for role, count in role_stats:
                logger.info(f"    - Rôle: {role or 'Non défini'}, Nombre: {count}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des rôles: {e}")
        return False

def check_application_routes():
    """Vérifie les routes de l'application en production"""
    try:
        # URL de base de l'application en production
        base_url = os.environ.get('PRODUCTION_APP_URL')
        if not base_url:
            logger.warning("⚠️ La variable d'environnement PRODUCTION_APP_URL n'est pas définie")
            logger.info("Pour vérifier les routes, définissez la variable d'environnement avec l'URL de l'application en production")
            return False
        
        # Liste des routes à vérifier
        routes = [
            "/subscription-choice",
            "/payment/subscribe/school",
            "/payment/select_school"
        ]
        
        logger.info("🌐 Vérification des routes en production:")
        for route in routes:
            url = f"{base_url}{route}"
            try:
                response = requests.get(url, allow_redirects=False)
                status = response.status_code
                redirect_url = response.headers.get('Location', 'Pas de redirection')
                
                if status == 200:
                    logger.info(f"  ✅ {route} - OK (200)")
                elif 300 <= status < 400:
                    logger.info(f"  ➡️ {route} - Redirection ({status}) vers {redirect_url}")
                else:
                    logger.warning(f"  ❌ {route} - Erreur ({status})")
            except Exception as e:
                logger.error(f"  ❌ {route} - Exception: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des routes: {e}")
        return False

def main():
    """Fonction principale du script de diagnostic"""
    logger.info("=" * 80)
    logger.info("DIAGNOSTIC DES ABONNEMENTS ÉCOLE EN PRODUCTION")
    logger.info("=" * 80)
    
    # Vérifier la connexion à la base de données
    if not check_database_connection():
        return
    
    # Afficher toutes les écoles
    logger.info("\n" + "=" * 40)
    logger.info("LISTE DE TOUTES LES ÉCOLES")
    logger.info("=" * 40)
    check_all_schools()
    
    # Vérifier les écoles avec abonnements actifs
    logger.info("\n" + "=" * 40)
    logger.info("ÉCOLES AVEC ABONNEMENT ACTIF")
    logger.info("=" * 40)
    schools_with_subscription = check_schools_with_subscriptions()
    
    # Afficher les détails des abonnements
    logger.info("\n" + "=" * 40)
    logger.info("DÉTAILS DES ABONNEMENTS PAR ÉCOLE")
    logger.info("=" * 40)
    check_subscription_details()
    
    # Afficher la répartition des rôles
    logger.info("\n" + "=" * 40)
    logger.info("RÉPARTITION DES RÔLES PAR ÉCOLE")
    logger.info("=" * 40)
    check_user_roles_by_school()
    
    # Vérifier les routes de l'application
    logger.info("\n" + "=" * 40)
    logger.info("VÉRIFICATION DES ROUTES")
    logger.info("=" * 40)
    check_application_routes()
    
    # Résumé final
    logger.info("\n" + "=" * 40)
    logger.info("RÉSUMÉ DU DIAGNOSTIC")
    logger.info("=" * 40)
    if schools_with_subscription:
        logger.info(f"✅ {len(schools_with_subscription)} école(s) avec abonnement actif détectée(s)")
        logger.info("Le système de détection des écoles avec abonnement semble fonctionner correctement.")
    else:
        logger.info("❌ Aucune école avec abonnement actif n'a été détectée")
        logger.info("Vérifiez les données d'abonnement dans la base de données.")
    
    logger.info("=" * 80)
    logger.info("FIN DU DIAGNOSTIC")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
    db_session.remove()
