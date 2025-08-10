"""
Migration pour ajouter les champs d'abonnement et de validation admin au modèle User
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuration temporaire pour la migration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classe_numerique.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def upgrade_database():
    """Ajouter les nouveaux champs d'abonnement à la table user"""
    
    # Créer les nouvelles colonnes
    try:
        # Système d'inscription payante et validation admin
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'pending';
        """)
        print("✅ Colonne subscription_status ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN subscription_type VARCHAR(20);
        """)
        print("✅ Colonne subscription_type ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN subscription_amount FLOAT;
        """)
        print("✅ Colonne subscription_amount ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN payment_date DATETIME;
        """)
        print("✅ Colonne payment_date ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN payment_reference VARCHAR(100);
        """)
        print("✅ Colonne payment_reference ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN approval_date DATETIME;
        """)
        print("✅ Colonne approval_date ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN approved_by INTEGER;
        """)
        print("✅ Colonne approved_by ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN subscription_expires DATETIME;
        """)
        print("✅ Colonne subscription_expires ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN rejection_reason TEXT;
        """)
        print("✅ Colonne rejection_reason ajoutée")
        
        db.engine.execute("""
            ALTER TABLE user ADD COLUMN notes TEXT;
        """)
        print("✅ Colonne notes ajoutée")
        
        # Mettre à jour les utilisateurs existants
        # Les admins sont automatiquement approuvés
        db.engine.execute("""
            UPDATE user SET subscription_status = 'approved' WHERE role = 'admin';
        """)
        print("✅ Statut des admins mis à jour")
        
        # Les enseignants existants sont mis en statut 'approved' pour la transition
        db.engine.execute("""
            UPDATE user SET 
                subscription_status = 'approved',
                subscription_type = 'teacher',
                subscription_amount = 40.0,
                approval_date = datetime('now')
            WHERE role = 'teacher';
        """)
        print("✅ Statut des enseignants existants mis à jour")
        
        # Les étudiants gardent le statut par défaut
        print("✅ Migration terminée avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration : {str(e)}")
        raise e

if __name__ == "__main__":
    print("🚀 Démarrage de la migration des champs d'abonnement...")
    with app.app_context():
        upgrade_database()
