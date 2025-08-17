#!/usr/bin/env python3
"""
Script de migration simple pour ajouter la colonne school_name
"""

import sqlite3
import os

def migrate_school_column():
    """Ajouter la colonne school_name à la table User"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    
    if not os.path.exists(db_path):
        print("Base de donnees non trouvee:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'school_name' not in columns:
            print("Ajout de la colonne school_name...")
            cursor.execute("ALTER TABLE user ADD COLUMN school_name VARCHAR(200)")
            conn.commit()
            print("Colonne school_name ajoutee avec succes!")
        else:
            print("La colonne school_name existe deja.")
        
        # Vérifier le résultat
        cursor.execute("PRAGMA table_info(user)")
        columns_after = [row[1] for row in cursor.fetchall()]
        print("Colonnes dans la table User:", columns_after)
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print("Nombre total d'utilisateurs:", user_count)
        
        conn.close()
        return True
        
    except Exception as e:
        print("Erreur lors de la migration:", str(e))
        return False

if __name__ == "__main__":
    print("Demarrage de la migration school_name...")
    success = migrate_school_column()
    
    if success:
        print("Migration terminee avec succes!")
    else:
        print("Echec de la migration.")
