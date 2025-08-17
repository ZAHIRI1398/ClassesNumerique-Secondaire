#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne school_name à la table User
"""

import os
import sys
from sqlalchemy import text

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def migrate_school_column():
    """Ajouter la colonne school_name à la table User si elle n'existe pas"""
    
    with app.app_context():
        try:
            # Vérifier si la colonne existe déjà
            result = db.session.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'school_name' not in columns:
                print("🔄 Ajout de la colonne school_name à la table User...")
                
                # Ajouter la colonne school_name
                db.session.execute(text("ALTER TABLE user ADD COLUMN school_name VARCHAR(200)"))
                db.session.commit()
                
                print("✅ Colonne school_name ajoutée avec succès !")
            else:
                print("✅ La colonne school_name existe déjà.")
            
            # Vérifier le résultat
            result = db.session.execute(text("PRAGMA table_info(user)"))
            columns_after = [row[1] for row in result.fetchall()]
            print(f"📊 Colonnes dans la table User : {columns_after}")
            
            # Compter les utilisateurs
            user_count = User.query.count()
            print(f"👥 Nombre total d'utilisateurs : {user_count}")
            
            # Afficher quelques exemples
            users_with_school = User.query.filter(User.school_name.isnot(None)).all()
            print(f"🏫 Utilisateurs avec école : {len(users_with_school)}")
            
            for user in users_with_school[:3]:  # Afficher les 3 premiers
                print(f"   - {user.name} ({user.email}) → {user.school_name}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration : {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Démarrage de la migration school_name...")
    success = migrate_school_column()
    
    if success:
        print("🎉 Migration terminée avec succès !")
    else:
        print("💥 Échec de la migration.")
        sys.exit(1)
