import os
import subprocess

# Définir la variable d'environnement
os.environ['PRODUCTION_DATABASE_URL'] = 'postgresql://postgres:SJqjLlGjIzLYjOuaKRcTmDqrgkMpcGJO@postgres.railway.internal:5432/railway'

# Exécuter le script
print("Vérification des statuts d'abonnement des écoles en production...")
subprocess.run(['python', 'check_subscription_statuses.py'])

input("\nAppuyez sur Entrée pour quitter...")
