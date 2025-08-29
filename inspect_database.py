#!/usr/bin/env python3
"""
Script pour inspecter la structure de la base de données
"""

import sqlite3
import os

def inspect_database():
    """Inspecte la structure de la base de données"""
    # Vérifier plusieurs emplacements possibles
    db_paths = [
        'instance/classes_numeriques.db',
        'instance/app.db', 
        'instance/site.db',
        'instance/classe_numerique.db',
        'classes_numeriques.db',
        'app.db'
    ]
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
            
        file_size = os.path.getsize(db_path)
        if file_size == 0:
            print(f"Base de données vide: {db_path} (0 bytes)")
            continue
            
        print(f"=== Inspection de la base de données: {db_path} ===")
        print(f"Taille du fichier: {file_size} bytes")
        print()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Lister toutes les tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"Tables trouvées: {len(tables)}")
            for table in tables:
                table_name = table[0]
                print(f"  - {table_name}")
                
                # Obtenir le schéma de la table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print(f"    Colonnes:")
                for col in columns:
                    col_name, col_type = col[1], col[2]
                    print(f"      - {col_name} ({col_type})")
                
                # Compter les enregistrements
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    Enregistrements: {count}")
                print()
            
            if not tables:
                print("Aucune table trouvée dans la base de données")
                
        except Exception as e:
            print(f"Erreur lors de l'inspection: {e}")
        finally:
            conn.close()
        
        print("=" * 50)
        print()
    
    print("Inspection terminée.")

if __name__ == "__main__":
    inspect_database()
