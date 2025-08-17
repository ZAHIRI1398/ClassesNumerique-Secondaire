#!/usr/bin/env python3
"""
Script pour créer un compte administrateur et approuver des utilisateurs existants
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def create_admin_user():
    """Créer un compte administrateur"""
    with app.app_context():
        try:
            # Vérifier si l'admin existe déjà
            admin_email = 'admin@classesnumeriques.com'
            admin_user = User.query.filter_by(email=admin_email).first()
            
            if admin_user:
                print(f"[OK] Compte admin existe déjà: {admin_email}")
                # S'assurer qu'il est approuvé
                admin_user.subscription_status = 'approved'
                admin_user.role = 'admin'
                db.session.commit()
                print("[OK] Statut admin mis à jour")
            else:
                # Créer le compte admin
                admin_user = User(
                    username='admin',
                    email=admin_email,
                    name='Administrateur',
                    password_hash=generate_password_hash('AdminSecure2024!'),
                    role='admin',
                    subscription_status='approved',
                    subscription_type='admin',
                    approved_by='system'
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"[OK] Compte administrateur créé: {admin_email}")
            
            # Approuver mr.zahiri@gmail.com s'il existe
            zahiri_user = User.query.filter_by(email='mr.zahiri@gmail.com').first()
            if zahiri_user:
                zahiri_user.subscription_status = 'approved'
                zahiri_user.subscription_type = 'teacher'
                zahiri_user.approved_by = 'admin'
                db.session.commit()
                print("[OK] Compte mr.zahiri@gmail.com approuvé")
            else:
                print("[INFO] Compte mr.zahiri@gmail.com non trouvé")
            
            print("\n[SUCCES] Configuration terminée !")
            print("[IDENTIFIANTS] Connexion admin:")
            print(f"   Email: {admin_email}")
            print("   Mot de passe: AdminSecure2024!")
            
        except Exception as e:
            print(f"[ERREUR] Erreur: {e}")

if __name__ == '__main__':
    create_admin_user()
