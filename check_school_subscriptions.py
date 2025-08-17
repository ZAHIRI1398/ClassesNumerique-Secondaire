#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnostic pour vérifier les écoles et leurs abonnements
Ce script permet de vérifier la détection des écoles avec abonnement actif
et d'afficher des informations détaillées sur les abonnements.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"check_school_subscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("check_school_subscriptions")

# Création d'une application Flask minimale pour le contexte
app = Flask(__name__)

# Configuration de la base de données
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///classe_numerique.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Initialisation de la base de données
engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

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
        logger.info("✅ Connexion à la base de données réussie")
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

def main():
    """Fonction principale du script de diagnostic"""
    logger.info("=" * 80)
    logger.info("DIAGNOSTIC DES ABONNEMENTS ÉCOLE")
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
