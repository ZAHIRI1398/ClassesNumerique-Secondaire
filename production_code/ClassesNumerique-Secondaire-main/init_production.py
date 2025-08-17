#!/usr/bin/env python3
"""
Script d'initialisation pour la production Railway
- Crée les tables si elles n'existent pas
- Ajoute les colonnes manquantes pour les paiements
- Crée le compte administrateur par défaut
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Ajouter le répertoire courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def init_production_db():
    """Initialiser la base de données pour la production"""
    
    with app.app_context():
        print("=== INITIALISATION BASE DE DONNEES PRODUCTION ===")
        
        try:
            # 1. Créer toutes les tables
            print("1. Création des tables...")
            db.create_all()
            print("   ✓ Tables créées avec succès")
            
            # 2. Vérifier et ajouter les colonnes manquantes
            print("2. Vérification des colonnes paiement...")
            
            # Tester si les colonnes existent
            try:
                test_user = User.query.first()
                if test_user:
                    # Tester l'accès aux colonnes de paiement
                    _ = test_user.payment_session_id
                    _ = test_user.payment_amount
                    _ = test_user.payment_date
                    _ = test_user.payment_reference
                    _ = test_user.approval_date
                    _ = test_user.approved_by
                    _ = test_user.subscription_expires
                    _ = test_user.rejection_reason
                    _ = test_user.notes
                print("   ✓ Colonnes paiement présentes")
            except Exception as e:
                print(f"   ⚠ Colonnes manquantes détectées: {e}")
                print("   → Ajout des colonnes...")
                
                # Ajouter les colonnes manquantes (pour PostgreSQL)
                try:
                    db.engine.execute("""
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS payment_session_id VARCHAR(255);
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS payment_amount FLOAT DEFAULT 0.0;
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS payment_date TIMESTAMP;
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS payment_reference VARCHAR(255);
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS approval_date TIMESTAMP;
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS approved_by INTEGER;
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS subscription_expires TIMESTAMP;
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
                        ALTER TABLE user ADD COLUMN IF NOT EXISTS notes TEXT;
                    """)
                    print("   ✓ Colonnes ajoutées avec succès")
                except Exception as alter_error:
                    print(f"   ⚠ Erreur lors de l'ajout des colonnes: {alter_error}")
            
            # 3. Créer le compte administrateur
            print("3. Création du compte administrateur...")
            
            # Vérifier si un admin existe déjà
            existing_admin = User.query.filter_by(role='admin').first()
            if existing_admin:
                print(f"   ✓ Admin existant trouvé: {existing_admin.email}")
            else:
                # Créer le compte admin par défaut
                admin_user = User(
                    name="Administrateur",
                    username="admin",
                    email="admin@admin.com",
                    password_hash=generate_password_hash("admin"),
                    role="admin",
                    subscription_status="approved",
                    subscription_type="admin",
                    subscription_amount=0.0,
                    created_at=datetime.now(),
                    approval_date=datetime.now(),
                    approved_by=1  # Auto-approuvé
                )
                
                db.session.add(admin_user)
                db.session.commit()
                print("   ✓ Compte admin créé: admin@admin.com / admin")
            
            # 4. Statistiques finales
            print("4. Statistiques de la base...")
            total_users = User.query.count()
            admins = User.query.filter_by(role='admin').count()
            teachers = User.query.filter_by(role='teacher').count()
            students = User.query.filter_by(role='student').count()
            
            print(f"   → Total utilisateurs: {total_users}")
            print(f"   → Administrateurs: {admins}")
            print(f"   → Enseignants: {teachers}")
            print(f"   → Étudiants: {students}")
            
            print("\n🎉 INITIALISATION TERMINÉE AVEC SUCCÈS!")
            print("Vous pouvez maintenant vous connecter avec:")
            print("   Email: admin@admin.com")
            print("   Mot de passe: admin")
            
        except Exception as e:
            print(f"❌ ERREUR lors de l'initialisation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    print("Démarrage de l'initialisation de la production...")
    success = init_production_db()
    if success:
        print("✅ Initialisation réussie!")
        sys.exit(0)
    else:
        print("❌ Initialisation échouée!")
        sys.exit(1)
