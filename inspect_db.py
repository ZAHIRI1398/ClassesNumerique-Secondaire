#!/usr/bin/env python3
"""
Script pour inspecter la structure de la base de données
"""

import sqlite3
import os

def inspect_database():
    """Inspecter la structure de la base de données"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    
    if not os.path.exists(db_path):
        print("Base de donnees non trouvee:", db_path)
        # Essayer d'autres emplacements
        possible_paths = [
            'database.db',
            'app.db',
            'instance/app.db',
            'site.db'
        ]
        
        for path in possible_paths:
            full_path = os.path.join(os.path.dirname(__file__), path)
            if os.path.exists(full_path):
                print("Base trouvee:", full_path)
                db_path = full_path
                break
        else:
            print("Aucune base de donnees trouvee")
            return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lister toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables dans la base:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Si on trouve une table user ou User
        for table_name in ['user', 'User', 'users', 'Users']:
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                if columns:
                    print(f"\nColonnes dans la table {table_name}:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                    break
            except:
                continue
        
        conn.close()
        return True
        
    except Exception as e:
        print("Erreur lors de l'inspection:", str(e))
        return False

if __name__ == "__main__":
    print("Inspection de la base de donnees...")
    inspect_database()
