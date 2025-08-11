#!/usr/bin/env python3
"""
Script de configuration pour la production
Initialise la base de données et crée le compte administrateur
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_production():
    """Configuration initiale pour la production"""
    try:
        # Import après ajout du path
        from app import app, db
        from models import User
        
        with app.app_context():
            print("🔧 Configuration de la production...")
            
            # Créer toutes les tables
            print("📊 Création des tables de base de données...")
            db.create_all()
            print("✅ Tables créées avec succès!")
            
            # Vérifier si un admin existe déjà
            existing_admin = User.query.filter_by(role='admin').first()
            if existing_admin:
                print(f"ℹ️  Un administrateur existe déjà: {existing_admin.email}")
                return
            
            # Créer le compte administrateur
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@classesnumeriques.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'AdminSecure2024!')
            
            print(f"👤 Création du compte administrateur: {admin_email}")
            
            admin_user = User(
                username='admin',
                email=admin_email,
                name='Administrateur Principal',
                role='admin',
                subscription_status='approved',
                subscription_type='admin',
                created_at=datetime.utcnow()
            )
            admin_user.set_password(admin_password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Compte administrateur créé avec succès!")
            print(f"📧 Email: {admin_email}")
            print(f"🔑 Mot de passe: {admin_password}")
            print("⚠️  IMPORTANT: Changez ce mot de passe après la première connexion!")
            
            print("\n🎉 Configuration de production terminée avec succès!")
            
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    setup_production()
