#!/usr/bin/env python3
"""
Script pour créer un accès administrateur fonctionnel
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

def create_admin_access():
    """Créer ou réinitialiser l'accès administrateur"""
    
    db_path = os.path.join('instance', 'app.db')
    
    if not os.path.exists(db_path):
        print("[ERROR] Base de donnees non trouvee")
        return False
    
    print("=== CREATION ACCES ADMINISTRATEUR ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier les admins existants
        cursor.execute("SELECT id, email, username FROM user WHERE role = 'admin'")
        existing_admins = cursor.fetchall()
        
        print("ADMINISTRATEURS EXISTANTS:")
        for admin_id, email, username in existing_admins:
            print(f"  - ID: {admin_id}, Email: {email}, Username: {username}")
        print()
        
        # Supprimer les anciens admins pour éviter les conflits
        cursor.execute("DELETE FROM user WHERE role = 'admin'")
        deleted_count = cursor.rowcount
        print(f"[INFO] {deleted_count} ancien(s) administrateur(s) supprime(s)")
        
        # Créer un nouvel administrateur avec des identifiants simples
        admin_email = "admin@admin.com"
        admin_username = "admin"
        admin_password = "admin"
        admin_name = "Administrateur"
        
        password_hash = generate_password_hash(admin_password)
        
        sql = """
        INSERT INTO user (
            username, email, name, password_hash, role, 
            subscription_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(sql, (
            admin_username,
            admin_email,
            admin_name,
            password_hash,
            'admin',
            'approved',
            datetime.now().isoformat()
        ))
        
        admin_id = cursor.lastrowid
        
        # Valider les changements
        conn.commit()
        
        print("[SUCCESS] NOUVEL ADMINISTRATEUR CREE!")
        print(f"  ID: {admin_id}")
        print(f"  Email: {admin_email}")
        print(f"  Username: {admin_username}")
        print(f"  Mot de passe: {admin_password}")
        print()
        print("[IMPORTANT] Utilisez ces identifiants pour vous connecter:")
        print(f"  Email/Username: {admin_email} OU {admin_username}")
        print(f"  Mot de passe: {admin_password}")
        print()
        print("URL d'administration: http://127.0.0.1:5000/admin/dashboard")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la creation: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    success = create_admin_access()
    if success:
        print("\n[SUCCESS] Vous pouvez maintenant vous connecter avec les nouveaux identifiants!")
    else:
        print("\n[ERROR] Creation echouee. Verifiez les erreurs ci-dessus.")
