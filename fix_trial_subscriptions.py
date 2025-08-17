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
    
    # 1. Afficher les abonnements de type 'Trial' ou 'trial'
    print("\n=== ABONNEMENTS DE TYPE 'TRIAL' ===")
    cursor.execute("""
        SELECT id, email, school_name, subscription_type, subscription_status
        FROM users
        WHERE subscription_type IN ('Trial', 'trial')
        ORDER BY school_name
    """)
    trial_users = cursor.fetchall()
    
    if not trial_users:
        print("Aucun utilisateur avec abonnement de type 'Trial' ou 'trial' trouvé.")
    else:
        print(tabulate(trial_users, headers=["ID", "Email", "École", "Type d'abonnement", "Statut"]))
        print(f"\nNombre total d'utilisateurs avec abonnement 'Trial': {len(trial_users)}")
    
    # 2. Vérifier les écoles avec des abonnements 'Trial' mais pas 'school'
    print("\n=== ÉCOLES AVEC ABONNEMENTS 'TRIAL' UNIQUEMENT ===")
    cursor.execute("""
        SELECT DISTINCT t.school_name
        FROM users t
        WHERE t.subscription_type IN ('Trial', 'trial')
        AND t.school_name IS NOT NULL
        AND t.school_name != ''
        AND NOT EXISTS (
            SELECT 1 FROM users s
            WHERE s.school_name = t.school_name
            AND s.subscription_type = 'school'
        )
        ORDER BY t.school_name
    """)
    trial_only_schools = cursor.fetchall()
    
    if not trial_only_schools:
        print("Aucune école avec uniquement des abonnements 'Trial' trouvée.")
    else:
        print(tabulate(trial_only_schools, headers=["École"]))
        print(f"\nNombre total d'écoles avec uniquement des abonnements 'Trial': {len(trial_only_schools)}")
    
    # 3. Option pour corriger les données
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("\n=== CORRECTION DES DONNÉES ===")
        
        # Mettre à jour les abonnements de type 'Trial' ou 'trial' en 'school'
        cursor.execute("""
            UPDATE users
            SET subscription_type = 'school'
            WHERE subscription_type IN ('Trial', 'trial')
            AND school_name IS NOT NULL
            AND school_name != ''
        """)
        
        rows_updated = cursor.rowcount
        print(f"Mise à jour du type d'abonnement pour {rows_updated} utilisateurs (Trial -> school).")
        
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
        print("python fix_trial_subscriptions.py --fix")
    
except Exception as e:
    print(f"Erreur lors de la connexion à la base de données: {str(e)}")
finally:
    if 'conn' in locals():
        conn.close()
