"""
Script pour corriger les données dans la base de données locale SQLite
- Correction du nom d'école "Ecole Bruxelles ll" en "École Bruxelles II"
- Mise à jour des types d'abonnement des utilisateurs associés à cette école de "trial" à "school"
"""

import os
import sqlite3
import logging
from datetime import datetime

# Configuration du logging
log_filename = f"update_local_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Chemin vers la base de données SQLite locale
DB_PATH = "instance/site.db"  # Ajustez si nécessaire

def connect_to_database():
    """Établit une connexion à la base de données SQLite locale"""
    try:
        if not os.path.exists(DB_PATH):
            logging.error(f"Base de données non trouvée: {DB_PATH}")
            return None
        
        conn = sqlite3.connect(DB_PATH)
        logging.info(f"Connexion établie à la base de données: {DB_PATH}")
        return conn
    except Exception as e:
        logging.error(f"Erreur de connexion à la base de données: {str(e)}")
        return None

def check_school_names(conn):
    """Vérifie les noms d'écoles dans la base de données"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT school_name FROM user WHERE school_name IS NOT NULL AND school_name != ''")
        schools = cursor.fetchall()
        
        logging.info(f"Écoles trouvées dans la base de données:")
        for school in schools:
            logging.info(f"- {school[0]}")
        
        return schools
    except Exception as e:
        logging.error(f"Erreur lors de la vérification des noms d'écoles: {str(e)}")
        return []

def check_users_with_school(conn, school_name):
    """Vérifie les utilisateurs associés à une école spécifique"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, role, subscription_type, subscription_status 
            FROM user 
            WHERE school_name = ?
        """, (school_name,))
        users = cursor.fetchall()
        
        logging.info(f"Utilisateurs associés à l'école '{school_name}':")
        for user in users:
            logging.info(f"- ID: {user[0]}, Email: {user[1]}, Rôle: {user[2]}, Type d'abonnement: {user[3]}, Statut: {user[4]}")
        
        return users
    except Exception as e:
        logging.error(f"Erreur lors de la vérification des utilisateurs: {str(e)}")
        return []

def update_school_name(conn, old_name, new_name):
    """Met à jour le nom d'une école dans la base de données"""
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET school_name = ? WHERE school_name = ?", (new_name, old_name))
        conn.commit()
        
        affected_rows = cursor.rowcount
        logging.info(f"Nom d'école mis à jour: '{old_name}' -> '{new_name}', {affected_rows} utilisateurs affectés")
        return affected_rows
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour du nom d'école: {str(e)}")
        conn.rollback()
        return 0

def update_subscription_type(conn, school_name, old_type, new_type):
    """Met à jour le type d'abonnement des utilisateurs associés à une école"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user 
            SET subscription_type = ? 
            WHERE school_name = ? AND subscription_type = ?
        """, (new_type, school_name, old_type))
        conn.commit()
        
        affected_rows = cursor.rowcount
        logging.info(f"Type d'abonnement mis à jour pour l'école '{school_name}': '{old_type}' -> '{new_type}', {affected_rows} utilisateurs affectés")
        return affected_rows
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour du type d'abonnement: {str(e)}")
        conn.rollback()
        return 0

def main():
    """Fonction principale pour exécuter les corrections"""
    logging.info("=== DÉBUT DE LA CORRECTION DE LA BASE DE DONNÉES LOCALE ===")
    
    # Connexion à la base de données
    conn = connect_to_database()
    if not conn:
        logging.error("Impossible de continuer sans connexion à la base de données")
        return
    
    try:
        # 1. Vérifier les noms d'écoles actuels
        logging.info("1. Vérification des noms d'écoles actuels")
        schools = check_school_names(conn)
        
        # 2. Rechercher spécifiquement "Ecole Bruxelles ll"
        old_school_name = "Ecole Bruxelles ll"
        new_school_name = "École Bruxelles II"
        
        school_exists = any(school[0] == old_school_name for school in schools)
        if school_exists:
            logging.info(f"École '{old_school_name}' trouvée dans la base de données")
            
            # 3. Vérifier les utilisateurs associés à cette école
            logging.info(f"3. Vérification des utilisateurs associés à l'école '{old_school_name}'")
            users_before = check_users_with_school(conn, old_school_name)
            
            # 4. Corriger le nom de l'école
            logging.info(f"4. Correction du nom de l'école: '{old_school_name}' -> '{new_school_name}'")
            updated_rows = update_school_name(conn, old_school_name, new_school_name)
            logging.info(f"Nombre d'utilisateurs avec école mise à jour: {updated_rows}")
            
            # 5. Mettre à jour le type d'abonnement des utilisateurs
            logging.info(f"5. Mise à jour du type d'abonnement des utilisateurs de l'école '{new_school_name}'")
            updated_subscriptions = update_subscription_type(conn, new_school_name, "trial", "school")
            logging.info(f"Nombre d'utilisateurs avec type d'abonnement mis à jour: {updated_subscriptions}")
            
            # 6. Vérifier les utilisateurs après mise à jour
            logging.info(f"6. Vérification des utilisateurs après mise à jour")
            users_after = check_users_with_school(conn, new_school_name)
            
            logging.info(f"Correction terminée pour l'école '{old_school_name}' -> '{new_school_name}'")
        else:
            logging.info(f"École '{old_school_name}' non trouvée dans la base de données")
            
            # Vérifier si la nouvelle version du nom existe déjà
            new_school_exists = any(school[0] == new_school_name for school in schools)
            if new_school_exists:
                logging.info(f"École '{new_school_name}' existe déjà dans la base de données")
                
                # Vérifier les utilisateurs associés à cette école
                logging.info(f"Vérification des utilisateurs associés à l'école '{new_school_name}'")
                users = check_users_with_school(conn, new_school_name)
                
                # Mettre à jour le type d'abonnement si nécessaire
                logging.info(f"Mise à jour du type d'abonnement des utilisateurs de l'école '{new_school_name}'")
                updated_subscriptions = update_subscription_type(conn, new_school_name, "trial", "school")
                logging.info(f"Nombre d'utilisateurs avec type d'abonnement mis à jour: {updated_subscriptions}")
            else:
                logging.info("Aucune correction nécessaire pour les noms d'écoles")
        
        # 7. Vérification finale
        logging.info("7. Vérification finale des écoles après corrections")
        final_schools = check_school_names(conn)
        
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution du script: {str(e)}")
    finally:
        conn.close()
        logging.info("Connexion à la base de données fermée")
    
    logging.info("=== FIN DE LA CORRECTION DE LA BASE DE DONNÉES LOCALE ===")

if __name__ == "__main__":
    main()
    print(f"Script terminé. Consultez le fichier de log '{log_filename}' pour plus de détails.")
