import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from tabulate import tabulate

# Charger les variables d'environnement
load_dotenv()

# Récupérer l'URL de la base de données de production
DATABASE_URL = os.environ.get('PRODUCTION_DATABASE_URL')

if not DATABASE_URL:
    print("Erreur: La variable d'environnement PRODUCTION_DATABASE_URL n'est pas définie.")
    print("Veuillez définir cette variable dans le fichier .env ou en ligne de commande.")
    sys.exit(1)

try:
    # Connexion à la base de données PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("\n=== VÉRIFICATION DES STATUTS D'ABONNEMENT DES ÉCOLES ===\n")
    
    # Requête pour obtenir toutes les écoles avec leurs statuts d'abonnement
    query = """
    SELECT 
        school_name, 
        subscription_status,
        COUNT(*) as user_count
    FROM 
        "user"
    WHERE 
        school_name IS NOT NULL 
        AND school_name != '' 
        AND subscription_type = 'school'
    GROUP BY 
        school_name, subscription_status
    ORDER BY 
        school_name, subscription_status
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("Aucune école avec abonnement n'a été trouvée dans la base de données.")
    else:
        # Organiser les résultats par école
        schools = {}
        for school_name, status, count in results:
            if school_name not in schools:
                schools[school_name] = []
            schools[school_name].append((status, count))
        
        # Afficher les résultats sous forme de tableau
        table_data = []
        for school, statuses in schools.items():
            status_str = ", ".join([f"{status} ({count})" for status, count in statuses])
            total_users = sum(count for _, count in statuses)
            table_data.append([school, status_str, total_users])
        
        print(tabulate(table_data, headers=["École", "Statuts (nombre d'utilisateurs)", "Total utilisateurs"], tablefmt="grid"))
        
        # Vérifier les écoles qui devraient être visibles dans la page de sélection
        visible_schools = []
        for school, statuses in schools.items():
            for status, _ in statuses:
                if status in ['pending', 'paid', 'approved']:
                    visible_schools.append(school)
                    break
        
        print("\n=== ÉCOLES QUI DEVRAIENT ÊTRE VISIBLES DANS LA PAGE DE SÉLECTION ===\n")
        if visible_schools:
            for school in visible_schools:
                print(f"- {school}")
        else:
            print("Aucune école ne devrait être visible dans la page de sélection.")
    
    # Fermer la connexion
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Erreur lors de la connexion à la base de données: {e}")
    sys.exit(1)
