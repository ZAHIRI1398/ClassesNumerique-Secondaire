#!/usr/bin/env python3
"""
Script de migration pour ajouter les colonnes manquantes du système de paiement
"""

import os
import sys
import sqlite3
from datetime import datetime

def migrate_payment_columns():
    """Ajouter les colonnes manquantes pour le système de paiement"""
    
    db_path = os.path.join('instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Base de donnees non trouvee: {db_path}")
        return False
    
    print(f"[MIGRATION] Base de donnees: {db_path}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"[INFO] Colonnes existantes dans 'user': {len(existing_columns)}")
        for col in existing_columns:
            print(f"  - {col}")
        print()
        
        # Colonnes à ajouter selon le modèle User
        new_columns = [
            ('subscription_status', 'VARCHAR(20) DEFAULT "pending"'),
            ('subscription_type', 'VARCHAR(20)'),
            ('subscription_amount', 'FLOAT'),
            ('payment_date', 'DATETIME'),
            ('payment_reference', 'VARCHAR(100)'),
            ('payment_session_id', 'VARCHAR(200)'),
            ('payment_amount', 'FLOAT'),
            ('approval_date', 'DATETIME'),
            ('approved_by', 'INTEGER'),
            ('subscription_expires', 'DATETIME'),
            ('rejection_reason', 'TEXT'),
            ('notes', 'TEXT')
        ]
        
        # Ajouter les colonnes manquantes
        columns_added = 0
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE user ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    print(f"[OK] Colonne ajoutee: {column_name} ({column_type})")
                    columns_added += 1
                except sqlite3.OperationalError as e:
                    print(f"[ERREUR] Erreur lors de l'ajout de {column_name}: {e}")
            else:
                print(f"[SKIP] Colonne deja existante: {column_name}")
        
        # Créer un utilisateur admin par défaut s'il n'existe pas
        cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print(f"\n[ADMIN] Creation d'un utilisateur administrateur par defaut...")
            from werkzeug.security import generate_password_hash
            
            admin_data = {
                'username': 'admin',
                'email': 'admin@classesnumeriques.com',
                'name': 'Administrateur',
                'password_hash': generate_password_hash('admin123'),
                'role': 'admin',
                'subscription_status': 'approved',
                'created_at': datetime.now().isoformat()
            }
            
            sql = """
            INSERT INTO user (username, email, name, password_hash, role, subscription_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(sql, (
                admin_data['username'],
                admin_data['email'],
                admin_data['name'],
                admin_data['password_hash'],
                admin_data['role'],
                admin_data['subscription_status'],
                admin_data['created_at']
            ))
            
            print(f"[OK] Administrateur cree:")
            print(f"   Email: {admin_data['email']}")
            print(f"   Mot de passe: admin123")
            print(f"   [IMPORTANT] CHANGEZ LE MOT DE PASSE APRES LA PREMIERE CONNEXION!")
        else:
            print(f"\n[INFO] {admin_count} administrateur(s) deja existant(s)")
        
        # Valider les changements
        conn.commit()
        
        print(f"\n[SUCCESS] MIGRATION TERMINEE AVEC SUCCES!")
        print(f"Colonnes ajoutees: {columns_added}")
        print(f"Base de donnees prete pour l'interface d'administration")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la migration: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    success = migrate_payment_columns()
    if success:
        print(f"\n[SUCCESS] Vous pouvez maintenant lancer l'audit des utilisateurs!")
    else:
        print(f"\n[ERROR] Migration echouee. Verifiez les erreurs ci-dessus.")
