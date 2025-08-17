#!/usr/bin/env python3
"""
Script pour restaurer le compte mr.zahiri@gmail.com avec droits admin
"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def restore_zahiri_account():
    with app.app_context():
        try:
            # Vérifier si le compte existe déjà
            existing_user = User.query.filter_by(email='mr.zahiri@gmail.com').first()
            
            if existing_user:
                print(f"Compte mr.zahiri@gmail.com existe deja (ID: {existing_user.id})")
                # Mettre à jour les droits admin au cas où
                existing_user.role = 'admin'
                existing_user.subscription_status = 'approved'
                existing_user.subscription_type = 'admin'
                existing_user.approved_by = 'system'
                db.session.commit()
                print("Droits admin mis a jour")
                return existing_user
            
            # Créer le compte mr.zahiri@gmail.com
            zahiri_user = User(
                username='mr.zahiri',
                email='mr.zahiri@gmail.com',
                name='Mr Aziz Zahiri',
                password_hash=generate_password_hash('zahiri123'),  # Mot de passe simple
                role='admin',  # Droits administrateur
                subscription_status='approved',
                subscription_type='admin',
                approved_by='system'
            )
            
            db.session.add(zahiri_user)
            db.session.commit()
            
            print(f"Compte mr.zahiri@gmail.com cree avec succes (ID: {zahiri_user.id})")
            print("Email: mr.zahiri@gmail.com")
            print("Mot de passe: zahiri123")
            print("Role: admin")
            print("Statut: approved")
            
            return zahiri_user
            
        except Exception as e:
            print(f"Erreur lors de la creation du compte: {e}")
            return None

if __name__ == '__main__':
    print("Restauration du compte mr.zahiri@gmail.com...")
    user = restore_zahiri_account()
    if user:
        print("Restauration terminee avec succes !")
    else:
        print("Echec de la restauration")
