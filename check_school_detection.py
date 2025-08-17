import sys
import psycopg2
from tabulate import tabulate

# URL de la base de données de production (extraite de run_fix_trial_subscriptions.bat)
db_url = "postgresql://postgres:SJqjLlGjIzLYjOuaKRcTmDqrgkMpcGJO@postgres.railway.internal:5432/railway"

# Vérifier si l'URL est accessible localement (peut nécessiter un tunnel SSH ou VPN)
print("Utilisation de l'URL de la base de données de production...")
print("Note: Cette URL peut ne pas être accessible directement depuis votre environnement local.")
print("Si la connexion échoue, vous devrez peut-être utiliser un tunnel SSH ou VPN vers Railway.")
print("Ou exécuter ce script directement sur le serveur de production.")
print("\n=== TENTATIVE DE CONNEXION ===\n")

try:
    # Connexion à la base de données
    print("Connexion à la base de données...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # 1. Vérifier tous les types d'abonnements dans la base
    print("\n=== TYPES D'ABONNEMENTS DANS LA BASE ===")
    cursor.execute("""
        SELECT DISTINCT subscription_type, COUNT(*) as count
        FROM users
        WHERE subscription_type IS NOT NULL
        GROUP BY subscription_type
        ORDER BY subscription_type
    """)
    subscription_types = cursor.fetchall()
    
    if not subscription_types:
        print("Aucun type d'abonnement trouvé.")
    else:
        print(tabulate(subscription_types, headers=["Type d'abonnement", "Nombre d'utilisateurs"]))
    
    # 2. Vérifier tous les statuts d'abonnements dans la base
    print("\n=== STATUTS D'ABONNEMENTS DANS LA BASE ===")
    cursor.execute("""
        SELECT DISTINCT subscription_status, COUNT(*) as count
        FROM users
        WHERE subscription_status IS NOT NULL
        GROUP BY subscription_status
        ORDER BY subscription_status
    """)
    subscription_statuses = cursor.fetchall()
    
    if not subscription_statuses:
        print("Aucun statut d'abonnement trouvé.")
    else:
        print(tabulate(subscription_statuses, headers=["Statut d'abonnement", "Nombre d'utilisateurs"]))
    
    # 3. Simuler la requête de sélection d'école
    print("\n=== SIMULATION DE LA REQUÊTE SELECT_SCHOOL ===")
    cursor.execute("""
        SELECT school_name, COUNT(*) as user_count
        FROM users
        WHERE school_name IS NOT NULL
        AND school_name != ''
        AND subscription_type IN ('school', 'Trial', 'trial')
        AND subscription_status IN ('pending', 'paid', 'approved')
        GROUP BY school_name
        ORDER BY school_name
    """)
    schools_with_subscription = cursor.fetchall()
    
    if not schools_with_subscription:
        print("Aucune école avec abonnement actif trouvée.")
    else:
        print(tabulate(schools_with_subscription, headers=["École", "Nombre d'utilisateurs"]))
        print(f"\nNombre total d'écoles avec abonnement: {len(schools_with_subscription)}")
    
    # 4. Vérifier les écoles avec abonnement 'school' uniquement
    print("\n=== ÉCOLES AVEC ABONNEMENT 'SCHOOL' UNIQUEMENT ===")
    cursor.execute("""
        SELECT school_name, COUNT(*) as user_count
        FROM users
        WHERE school_name IS NOT NULL
        AND school_name != ''
        AND subscription_type = 'school'
        AND subscription_status IN ('pending', 'paid', 'approved')
        GROUP BY school_name
        ORDER BY school_name
    """)
    schools_with_school_subscription = cursor.fetchall()
    
    if not schools_with_school_subscription:
        print("Aucune école avec abonnement 'school' trouvée.")
    else:
        print(tabulate(schools_with_school_subscription, headers=["École", "Nombre d'utilisateurs"]))
        print(f"\nNombre total d'écoles avec abonnement 'school': {len(schools_with_school_subscription)}")
    
    # 5. Vérifier les écoles avec abonnement 'Trial' ou 'trial' uniquement
    print("\n=== ÉCOLES AVEC ABONNEMENT 'TRIAL' UNIQUEMENT ===")
    cursor.execute("""
        SELECT school_name, COUNT(*) as user_count
        FROM users
        WHERE school_name IS NOT NULL
        AND school_name != ''
        AND subscription_type IN ('Trial', 'trial')
        AND subscription_status IN ('pending', 'paid', 'approved')
        GROUP BY school_name
        ORDER BY school_name
    """)
    schools_with_trial_subscription = cursor.fetchall()
    
    if not schools_with_trial_subscription:
        print("Aucune école avec abonnement 'Trial' trouvée.")
    else:
        print(tabulate(schools_with_trial_subscription, headers=["École", "Nombre d'utilisateurs"]))
        print(f"\nNombre total d'écoles avec abonnement 'Trial': {len(schools_with_trial_subscription)}")
    
    # 6. Vérifier les écoles avec statut 'approved' uniquement
    print("\n=== ÉCOLES AVEC STATUT 'APPROVED' UNIQUEMENT ===")
    cursor.execute("""
        SELECT school_name, subscription_type, COUNT(*) as user_count
        FROM users
        WHERE school_name IS NOT NULL
        AND school_name != ''
        AND subscription_status = 'approved'
        GROUP BY school_name, subscription_type
        ORDER BY school_name
    """)
    schools_with_approved_status = cursor.fetchall()
    
    if not schools_with_approved_status:
        print("Aucune école avec statut 'approved' trouvée.")
    else:
        print(tabulate(schools_with_approved_status, headers=["École", "Type d'abonnement", "Nombre d'utilisateurs"]))
        print(f"\nNombre total d'écoles avec statut 'approved': {len(schools_with_approved_status)}")

except Exception as e:
    print(f"Erreur lors de la connexion à la base de données: {str(e)}")
finally:
    if 'conn' in locals():
        conn.close()
