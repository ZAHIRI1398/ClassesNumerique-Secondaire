import os
import sys
import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate

# Charger les variables d'environnement
load_dotenv()

# Récupérer l'URL de la base de données depuis les variables d'environnement
db_url = os.environ.get('PRODUCTION_DATABASE_URL')

if not db_url:
    print("Erreur: La variable d'environnement PRODUCTION_DATABASE_URL n'est pas définie.")
    print("Veuillez définir cette variable dans le fichier .env ou en ligne de commande.")
    sys.exit(1)

try:
    # Connexion à la base de données
    print("Connexion à la base de données...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # 1. Afficher toutes les écoles avec leurs statuts d'abonnement
    print("\n=== ÉCOLES ET STATUTS D'ABONNEMENT ACTUELS ===")
    cursor.execute("""
        SELECT DISTINCT school_name, subscription_type, subscription_status, COUNT(*) as user_count
        FROM users
        WHERE school_name IS NOT NULL AND school_name != ''
        GROUP BY school_name, subscription_type, subscription_status
        ORDER BY school_name
    """)
    schools = cursor.fetchall()
    
    if not schools:
        print("Aucune école trouvée dans la base de données.")
    else:
        print(tabulate(schools, headers=["Nom de l'école", "Type d'abonnement", "Statut", "Nombre d'utilisateurs"]))
    
    # 2. Vérifier les écoles qui devraient apparaître dans la sélection
    print("\n=== ÉCOLES QUI DEVRAIENT APPARAÎTRE DANS LA SÉLECTION ===")
    cursor.execute("""
        SELECT DISTINCT school_name, subscription_type, subscription_status, COUNT(*) as user_count
        FROM users
        WHERE school_name IS NOT NULL 
        AND school_name != ''
        AND subscription_type = 'school'
        AND subscription_status IN ('pending', 'paid', 'approved')
        GROUP BY school_name, subscription_type, subscription_status
        ORDER BY school_name
    """)
    eligible_schools = cursor.fetchall()
    
    if not eligible_schools:
        print("Aucune école éligible trouvée (avec statut pending, paid ou approved).")
    else:
        print(tabulate(eligible_schools, headers=["Nom de l'école", "Type d'abonnement", "Statut", "Nombre d'utilisateurs"]))
    
    # 3. Option pour corriger les données
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("\n=== CORRECTION DES DONNÉES ===")
        
        # Mettre à jour les écoles qui ont un abonnement mais pas le bon type
        cursor.execute("""
            UPDATE users
            SET subscription_type = 'school'
            WHERE school_name IS NOT NULL 
            AND school_name != ''
            AND subscription_status IN ('pending', 'paid', 'approved')
            AND subscription_type != 'school'
        """)
        
        rows_updated = cursor.rowcount
        print(f"Mise à jour du type d'abonnement pour {rows_updated} utilisateurs.")
        
        # Mettre à jour les écoles qui ont un type 'school' mais pas de statut valide
        cursor.execute("""
            UPDATE users
            SET subscription_status = 'approved'
            WHERE school_name IS NOT NULL 
            AND school_name != ''
            AND subscription_type = 'school'
            AND (subscription_status IS NULL OR subscription_status NOT IN ('pending', 'paid', 'approved'))
        """)
        
        rows_updated = cursor.rowcount
        print(f"Mise à jour du statut d'abonnement pour {rows_updated} utilisateurs.")
        
        # Valider les modifications
        conn.commit()
        print("Modifications enregistrées avec succès.")
        
        # Afficher les écoles éligibles après correction
        print("\n=== ÉCOLES ÉLIGIBLES APRÈS CORRECTION ===")
        cursor.execute("""
            SELECT DISTINCT school_name, subscription_type, subscription_status, COUNT(*) as user_count
            FROM users
            WHERE school_name IS NOT NULL 
            AND school_name != ''
            AND subscription_type = 'school'
            AND subscription_status IN ('pending', 'paid', 'approved')
            GROUP BY school_name, subscription_type, subscription_status
            ORDER BY school_name
        """)
        eligible_schools_after = cursor.fetchall()
        
        if not eligible_schools_after:
            print("Aucune école éligible trouvée après correction.")
        else:
            print(tabulate(eligible_schools_after, headers=["Nom de l'école", "Type d'abonnement", "Statut", "Nombre d'utilisateurs"]))
    else:
        print("\nPour corriger les données, exécutez le script avec l'option --fix:")
        print("python update_school_subscription.py --fix")
    
except Exception as e:
    print(f"Erreur lors de la connexion à la base de données: {str(e)}")
finally:
    if 'conn' in locals():
        conn.close()
