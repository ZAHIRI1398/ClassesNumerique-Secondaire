import os
import sys
import psycopg2
from psycopg2 import sql
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_production_database.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Récupérer l'URL de la base de données depuis les variables d'environnement
# ou utiliser une valeur par défaut pour le développement local
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/classenumerique')

# Si l'URL commence par postgres://, la convertir en postgresql:// (nécessaire pour psycopg2)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

logging.info(f"Connexion à la base de données: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Base locale'}")

try:
    # Connexion à la base de données
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    logging.info("Connexion à la base de données établie avec succès")
    
    # 1. Correction du nom de l'école
    old_school_name = "Ecole Bruxelles ll"
    new_school_name = "École Bruxelles II"
    
    # Vérifier si l'ancien nom existe
    cursor.execute("SELECT COUNT(*) FROM users WHERE school_name = %s", (old_school_name,))
    count = cursor.fetchone()[0]
    
    if count > 0:
        # Mettre à jour le nom de l'école
        cursor.execute("UPDATE users SET school_name = %s WHERE school_name = %s", (new_school_name, old_school_name))
        logging.info(f"Nom d'école mis à jour: {old_school_name} -> {new_school_name} ({cursor.rowcount} utilisateurs affectés)")
    else:
        # Vérifier si le nouveau nom existe déjà
        cursor.execute("SELECT COUNT(*) FROM users WHERE school_name = %s", (new_school_name,))
        count = cursor.fetchone()[0]
        if count > 0:
            logging.info(f"L'école avec le nom corrigé existe déjà: {new_school_name} ({count} utilisateurs)")
        else:
            logging.warning(f"Aucune école trouvée avec le nom: {old_school_name} ou {new_school_name}")
    
    # 2. Correction du type d'abonnement
    cursor.execute("""
        UPDATE users 
        SET subscription_type = 'school', subscription_amount = 99.99
        WHERE school_name = %s AND subscription_type = 'trial' AND subscription_status = 'approved'
    """, (new_school_name,))
    
    logging.info(f"Type d'abonnement mis à jour: trial -> school ({cursor.rowcount} utilisateurs affectés)")
    
    # 3. Vérification finale
    cursor.execute("""
        SELECT id, username, email, school_name, subscription_type, subscription_status, subscription_amount
        FROM users
        WHERE school_name = %s
    """, (new_school_name,))
    
    users = cursor.fetchall()
    logging.info(f"Utilisateurs associés à l'école {new_school_name}:")
    for user in users:
        logging.info(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, École: {user[3]}, Type: {user[4]}, Status: {user[5]}, Montant: {user[6]}")
    
    # 4. Vérification des écoles avec abonnement actif
    cursor.execute("""
        SELECT school_name, COUNT(*) as user_count
        FROM users
        WHERE school_name IS NOT NULL 
        AND school_name != ''
        AND subscription_type = 'school'
        AND subscription_status = 'approved'
        GROUP BY school_name
    """)
    
    schools = cursor.fetchall()
    logging.info("Écoles avec abonnement actif après correction:")
    for school in schools:
        logging.info(f"École: {school[0]}, Nombre d'utilisateurs: {school[1]}")
    
    # Valider les changements
    conn.commit()
    logging.info("Toutes les modifications ont été validées avec succès")

except Exception as e:
    logging.error(f"Erreur lors de la mise à jour de la base de données: {e}")
    if 'conn' in locals() and conn is not None:
        conn.rollback()
        logging.info("Rollback effectué")
finally:
    if 'cursor' in locals() and cursor is not None:
        cursor.close()
    if 'conn' in locals() and conn is not None:
        conn.close()
        logging.info("Connexion à la base de données fermée")

logging.info("Script terminé")
