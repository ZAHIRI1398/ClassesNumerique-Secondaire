#!/usr/bin/env python3
"""
Script pour ajouter la colonne school_name à la base de données existante
"""

import sqlite3
import os

def fix_school_column():
    """Ajouter la colonne school_name à la base de données existante"""
    
    # Chercher la base de données
    possible_paths = [
        'instance/database.db',
        'database.db',
        'app.db',
        'instance/app.db'
    ]
    
    db_path = None
    for path in possible_paths:
        full_path = os.path.join(os.path.dirname(__file__), path)
        if os.path.exists(full_path):
            db_path = full_path
            print(f"Base de donnees trouvee: {db_path}")
            break
    
    if not db_path:
        print("Aucune base de donnees trouvee")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier les tables existantes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables trouvees: {tables}")
        
        if 'user' not in tables:
            print("Table 'user' non trouvee")
            return False
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Colonnes existantes: {columns}")
        
        if 'school_name' not in columns:
            print("Ajout de la colonne school_name...")
            cursor.execute("ALTER TABLE user ADD COLUMN school_name VARCHAR(200)")
            conn.commit()
            print("Colonne school_name ajoutee avec succes!")
        else:
            print("La colonne school_name existe deja")
        
        # Vérifier le résultat final
        cursor.execute("PRAGMA table_info(user)")
        columns_after = [row[1] for row in cursor.fetchall()]
        print(f"Colonnes apres migration: {columns_after}")
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"Nombre d'utilisateurs: {user_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("=== MIGRATION COLONNE SCHOOL_NAME ===")
    success = fix_school_column()
    
    if success:
        print("=== MIGRATION REUSSIE ===")
    else:
        print("=== MIGRATION ECHOUEE ===")
