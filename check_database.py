"""
Script pour examiner la structure des bases de données SQLite locales
"""

import os
import sqlite3
import logging
from datetime import datetime

# Configuration du logging
log_filename = f"check_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Liste des bases de données à examiner
DB_PATHS = [
    "app.db",
    "instance/app.db",
    "instance/classe_numerique.db",
    "instance/site.db"
]

def check_database(db_path):
    """Examine la structure d'une base de données SQLite"""
    if not os.path.exists(db_path):
        print(f"Base de données non trouvée: {db_path}")
        logging.warning(f"Base de données non trouvée: {db_path}")
        return
    
    print(f"\n=== Examen de la base de données: {db_path} ===")
    logging.info(f"Examen de la base de données: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lister les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Tables dans {db_path}:")
        logging.info(f"Tables dans {db_path}:")
        
        for table in tables:
            table_name = table[0]
            print(f"- {table_name}")
            logging.info(f"- {table_name}")
            
            # Vérifier si c'est une table utilisateur
            if table_name.lower() in ['user', 'users']:
                # Lister les colonnes
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print(f"  Colonnes de la table {table_name}:")
                logging.info(f"  Colonnes de la table {table_name}:")
                
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                    logging.info(f"  - {col[1]} ({col[2]})")
                
                # Vérifier si la table contient des informations sur les écoles
                if any(col[1] == 'school_name' for col in columns):
                    print(f"  La table {table_name} contient des informations sur les écoles")
                    logging.info(f"  La table {table_name} contient des informations sur les écoles")
                    
                    # Vérifier les écoles
                    try:
                        cursor.execute(f"SELECT DISTINCT school_name FROM {table_name} WHERE school_name IS NOT NULL AND school_name != ''")
                        schools = cursor.fetchall()
                        
                        print(f"  Écoles trouvées dans la table {table_name}:")
                        logging.info(f"  Écoles trouvées dans la table {table_name}:")
                        
                        for school in schools:
                            print(f"  - {school[0]}")
                            logging.info(f"  - {school[0]}")
                            
                            # Vérifier les utilisateurs de cette école
                            cursor.execute(f"""
                                SELECT id, email, role, subscription_type, subscription_status 
                                FROM {table_name} 
                                WHERE school_name = ?
                            """, (school[0],))
                            users = cursor.fetchall()
                            
                            print(f"    Utilisateurs de l'école '{school[0]}': {len(users)}")
                            logging.info(f"    Utilisateurs de l'école '{school[0]}': {len(users)}")
                            
                            for user in users:
                                print(f"    - ID: {user[0]}, Email: {user[1]}, Rôle: {user[2]}, Type: {user[3]}, Statut: {user[4]}")
                                logging.info(f"    - ID: {user[0]}, Email: {user[1]}, Rôle: {user[2]}, Type: {user[3]}, Statut: {user[4]}")
                    except Exception as e:
                        print(f"  Erreur lors de la vérification des écoles: {str(e)}")
                        logging.error(f"  Erreur lors de la vérification des écoles: {str(e)}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors de l'examen de la base de données {db_path}: {str(e)}")
        logging.error(f"Erreur lors de l'examen de la base de données {db_path}: {str(e)}")

def main():
    """Fonction principale"""
    print("=== DÉBUT DE L'EXAMEN DES BASES DE DONNÉES ===")
    logging.info("=== DÉBUT DE L'EXAMEN DES BASES DE DONNÉES ===")
    
    for db_path in DB_PATHS:
        check_database(db_path)
    
    print("\n=== FIN DE L'EXAMEN DES BASES DE DONNÉES ===")
    logging.info("=== FIN DE L'EXAMEN DES BASES DE DONNÉES ===")
    print(f"Consultez le fichier de log '{log_filename}' pour plus de détails.")

if __name__ == "__main__":
    main()
