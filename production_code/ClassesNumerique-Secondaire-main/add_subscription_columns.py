"""
Script simple pour ajouter les colonnes d'abonnement à la base de données SQLite
"""

import sqlite3
import os

def add_subscription_columns():
    """Ajouter les colonnes d'abonnement à la table user"""
    
    # Chemin vers la base de données
    db_path = 'instance/app.db'
    
    if not os.path.exists(db_path):
        print(f"[ERREUR] Base de donnees {db_path} non trouvee")
        return
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("[INFO] Ajout des colonnes d'abonnement...")
        
        # Liste des colonnes à ajouter
        columns_to_add = [
            ("subscription_status", "VARCHAR(20) DEFAULT 'pending'"),
            ("subscription_type", "VARCHAR(20)"),
            ("subscription_amount", "REAL"),
            ("payment_date", "DATETIME"),
            ("payment_reference", "VARCHAR(100)"),
            ("approval_date", "DATETIME"),
            ("approved_by", "INTEGER"),
            ("subscription_expires", "DATETIME"),
            ("rejection_reason", "TEXT"),
            ("notes", "TEXT")
        ]
        
        # Ajouter chaque colonne
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE user ADD COLUMN {column_name} {column_type}")
                print(f"[OK] Colonne {column_name} ajoutee")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"[WARNING] Colonne {column_name} existe deja")
                else:
                    print(f"[ERREUR] Erreur pour {column_name}: {e}")
        
        # Mettre à jour les utilisateurs existants
        print("\n[INFO] Mise a jour des utilisateurs existants...")
        
        # Les admins sont automatiquement approuvés
        cursor.execute("""
            UPDATE user SET subscription_status = 'approved' 
            WHERE role = 'admin'
        """)
        print("[OK] Statut des admins mis a jour")
        
        # Les enseignants existants sont mis en statut 'approved' pour la transition
        cursor.execute("""
            UPDATE user SET 
                subscription_status = 'approved',
                subscription_type = 'teacher',
                subscription_amount = 40.0,
                approval_date = datetime('now')
            WHERE role = 'teacher'
        """)
        print("[OK] Statut des enseignants existants mis a jour")
        
        # Valider les changements
        conn.commit()
        print("\n[SUCCESS] Migration terminee avec succes !")
        
        # Vérifier les résultats
        cursor.execute("SELECT COUNT(*) FROM user WHERE subscription_status = 'approved'")
        approved_count = cursor.fetchone()[0]
        print(f"[STATS] Nombre d'utilisateurs approuves : {approved_count}")
        
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la migration : {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_subscription_columns()
