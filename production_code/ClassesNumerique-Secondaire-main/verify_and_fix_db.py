#!/usr/bin/env python3
"""
Script pour vérifier et corriger définitivement la base de données
"""

import sqlite3
import os

def verify_and_fix_database():
    """Vérifier et corriger la base de données"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    
    print(f"Verification de la base: {db_path}")
    print(f"Fichier existe: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("ERREUR: Base de donnees non trouvee!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        if 'user' not in tables:
            print("ERREUR: Table 'user' manquante!")
            conn.close()
            return False
        
        # Vérifier les colonnes de la table user
        cursor.execute("PRAGMA table_info(user)")
        columns_info = cursor.fetchall()
        columns = [row[1] for row in columns_info]
        
        print("Colonnes dans 'user':")
        for col_info in columns_info:
            print(f"  - {col_info[1]} ({col_info[2]})")
        
        # Vérifier spécifiquement school_name
        if 'school_name' not in columns:
            print("ATTENTION: Colonne 'school_name' manquante!")
            print("Ajout de la colonne school_name...")
            
            cursor.execute("ALTER TABLE user ADD COLUMN school_name VARCHAR(200)")
            conn.commit()
            print("Colonne school_name ajoutee!")
            
            # Re-vérifier
            cursor.execute("PRAGMA table_info(user)")
            new_columns = [row[1] for row in cursor.fetchall()]
            print(f"Nouvelles colonnes: {new_columns}")
        else:
            print("OK: Colonne 'school_name' presente!")
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"Nombre d'utilisateurs: {user_count}")
        
        # Tester une requête avec school_name
        try:
            cursor.execute("SELECT id, email, school_name FROM user LIMIT 3")
            users = cursor.fetchall()
            print("Test requete school_name:")
            for user in users:
                print(f"  - ID: {user[0]}, Email: {user[1]}, Ecole: {user[2]}")
        except Exception as e:
            print(f"ERREUR test requete: {e}")
            conn.close()
            return False
        
        conn.close()
        print("Base de donnees OK!")
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("=== VERIFICATION ET CORRECTION BASE ===")
    success = verify_and_fix_database()
    
    if success:
        print("=== BASE DE DONNEES OK ===")
    else:
        print("=== PROBLEME BASE DE DONNEES ===")
