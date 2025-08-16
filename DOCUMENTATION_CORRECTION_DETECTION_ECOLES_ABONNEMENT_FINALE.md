# Documentation : Correction de la détection des écoles avec abonnement

## Problème initial

L'application ne détectait pas correctement les écoles avec des abonnements actifs, ce qui entraînait :
- Des redirections en boucle vers la page de paiement pour les enseignants
- Le message "Aucune école avec un abonnement actif n'a été trouvée" malgré des abonnements existants
- Impossibilité pour les enseignants de s'associer à leur école

## Causes identifiées

Après analyse approfondie, trois causes principales ont été identifiées :

1. **Différence de nom d'école** : L'école "École Bruxelles II" était enregistrée comme "Ecole Bruxelles ll" (sans accent, avec des 'l' minuscules au lieu de 'I' majuscules)
2. **Type d'abonnement incorrect** : Les utilisateurs associés à l'école avaient `subscription_type='trial'` au lieu de `'school'`
3. **Filtre SQL trop restrictif** : Le code filtrait sur `subscription_status` avec les valeurs `['paid', 'approved']` alors que seul `'approved'` est utilisé en production

## Solutions implémentées

### 1. Correction du code dans payment_routes.py

Le code a été modifié pour ne filtrer que sur le statut `'approved'` au lieu de `['paid', 'approved']` :

```python
# AVANT
schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
    filter(User.school_name != None).\
    filter(User.school_name != '').\
    filter(User.subscription_type == 'school').\
    filter(User.subscription_status.in_(['paid', 'approved'])).\
    group_by(User.school_name).all()

# APRÈS
schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
    filter(User.school_name != None).\
    filter(User.school_name != '').\
    filter(User.subscription_type == 'school').\
    filter(User.subscription_status == 'approved').\
    group_by(User.school_name).all()
```

De même pour la route `join_school` :

```python
# AVANT
school_subscription = User.query.filter(
    User.school_name == school_name,
    User.subscription_type == 'school',
    User.subscription_status.in_(['paid', 'approved'])
).first()

# APRÈS
school_subscription = User.query.filter(
    User.school_name == school_name,
    User.subscription_type == 'school',
    User.subscription_status == 'approved'
).first()
```

### 2. Correction des données dans la base de données locale

Un script `fix_local_database.py` a été créé pour corriger les données dans la base SQLite locale :

```python
import sqlite3
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_local_database.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Connexion à la base de données
try:
    conn = sqlite3.connect('instance/classe_numerique.db')
    cursor = conn.cursor()
    logger.info("Connexion à la base de données réussie")
except Exception as e:
    logger.error(f"Erreur de connexion à la base de données: {e}")
    exit(1)

# Vérification des écoles existantes
cursor.execute("SELECT DISTINCT school_name FROM user WHERE school_name IS NOT NULL")
schools = cursor.fetchall()
logger.info(f"Écoles trouvées dans la base de données: {schools}")

# Correction du nom d'école
old_school_name = "Ecole Bruxelles ll"
new_school_name = "École Bruxelles II"

cursor.execute("SELECT COUNT(*) FROM user WHERE school_name = ?", (old_school_name,))
count_before = cursor.fetchone()[0]
logger.info(f"Nombre d'utilisateurs avec l'ancien nom d'école '{old_school_name}': {count_before}")

if count_before > 0:
    cursor.execute("UPDATE user SET school_name = ? WHERE school_name = ?", (new_school_name, old_school_name))
    conn.commit()
    logger.info(f"Nom d'école mis à jour: '{old_school_name}' -> '{new_school_name}'")
else:
    logger.info(f"Aucun utilisateur trouvé avec le nom d'école '{old_school_name}'")

# Correction du type d'abonnement
cursor.execute("SELECT COUNT(*) FROM user WHERE school_name = ? AND subscription_type = 'trial'", (new_school_name,))
count_trial = cursor.fetchone()[0]
logger.info(f"Nombre d'utilisateurs de l'école '{new_school_name}' avec subscription_type='trial': {count_trial}")

if count_trial > 0:
    cursor.execute("UPDATE user SET subscription_type = 'school' WHERE school_name = ? AND subscription_type = 'trial'", (new_school_name,))
    conn.commit()
    logger.info(f"Type d'abonnement mis à jour pour {count_trial} utilisateurs: 'trial' -> 'school'")
else:
    logger.info(f"Aucun utilisateur de l'école '{new_school_name}' avec subscription_type='trial'")

# Vérification des modifications
cursor.execute("SELECT DISTINCT school_name, subscription_type, subscription_status FROM user WHERE school_name = ?", (new_school_name,))
updated_schools = cursor.fetchall()
logger.info(f"École après mise à jour: {updated_schools}")

# Fermeture de la connexion
conn.close()
logger.info("Opération terminée avec succès")
```

### 3. Ajout de logs de débogage

Des logs de débogage détaillés ont été ajoutés dans les routes `select_school` et `join_school` pour faciliter le diagnostic :

```python
# Dans select_school
app.logger.debug(f"Schools with subscription: {schools_with_subscription}")
for school in schools_with_subscription:
    app.logger.debug(f"School: {school.school_name}, Users: {school.user_count}")

# Dans join_school
app.logger.debug(f"Checking subscription for school: {school_name}")
app.logger.debug(f"School subscription found: {school_subscription}")
if school_subscription:
    app.logger.debug(f"School subscription details: Type={school_subscription.subscription_type}, Status={school_subscription.subscription_status}")
```

## Tests et validation

1. **Vérification de la base de données** : Les données ont été corrigées avec succès :
   - Nom d'école : "Ecole Bruxelles ll" → "École Bruxelles II"
   - Type d'abonnement : "trial" → "school"
   - Statut d'abonnement : "approved" (inchangé)

2. **Test de l'application locale** : L'application détecte maintenant correctement les écoles avec abonnement :
   - La liste des écoles avec abonnement inclut "École Bruxelles II"
   - Les enseignants peuvent s'associer à l'école sans redirection en boucle
   - Le message "Aucune école avec un abonnement actif n'a été trouvée" ne s'affiche plus

## Recommandations pour la production

Pour appliquer ces corrections en production :

1. **Mettre à jour le code** : Déployer les modifications de `payment_routes.py` pour filtrer uniquement sur `subscription_status == 'approved'`

2. **Corriger les données** : Adapter le script `fix_local_database.py` pour PostgreSQL et l'exécuter sur la base de données de production :

```python
import psycopg2
import os
from dotenv import load_dotenv
import logging

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_production_database.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Connexion à la base de données PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    cursor = conn.cursor()
    logger.info("Connexion à la base de données PostgreSQL réussie")
except Exception as e:
    logger.error(f"Erreur de connexion à la base de données: {e}")
    exit(1)

# Vérification des écoles existantes
cursor.execute("SELECT DISTINCT school_name FROM \"user\" WHERE school_name IS NOT NULL")
schools = cursor.fetchall()
logger.info(f"Écoles trouvées dans la base de données: {schools}")

# Correction du nom d'école
old_school_name = "Ecole Bruxelles ll"
new_school_name = "École Bruxelles II"

cursor.execute("SELECT COUNT(*) FROM \"user\" WHERE school_name = %s", (old_school_name,))
count_before = cursor.fetchone()[0]
logger.info(f"Nombre d'utilisateurs avec l'ancien nom d'école '{old_school_name}': {count_before}")

if count_before > 0:
    cursor.execute("UPDATE \"user\" SET school_name = %s WHERE school_name = %s", (new_school_name, old_school_name))
    conn.commit()
    logger.info(f"Nom d'école mis à jour: '{old_school_name}' -> '{new_school_name}'")
else:
    logger.info(f"Aucun utilisateur trouvé avec le nom d'école '{old_school_name}'")

# Correction du type d'abonnement
cursor.execute("SELECT COUNT(*) FROM \"user\" WHERE school_name = %s AND subscription_type = 'trial'", (new_school_name,))
count_trial = cursor.fetchone()[0]
logger.info(f"Nombre d'utilisateurs de l'école '{new_school_name}' avec subscription_type='trial': {count_trial}")

if count_trial > 0:
    cursor.execute("UPDATE \"user\" SET subscription_type = 'school' WHERE school_name = %s AND subscription_type = 'trial'", (new_school_name,))
    conn.commit()
    logger.info(f"Type d'abonnement mis à jour pour {count_trial} utilisateurs: 'trial' -> 'school'")
else:
    logger.info(f"Aucun utilisateur de l'école '{new_school_name}' avec subscription_type='trial'")

# Vérification des modifications
cursor.execute("SELECT DISTINCT school_name, subscription_type, subscription_status FROM \"user\" WHERE school_name = %s", (new_school_name,))
updated_schools = cursor.fetchall()
logger.info(f"École après mise à jour: {updated_schools}")

# Fermeture de la connexion
conn.close()
logger.info("Opération terminée avec succès")
```

## Prévention des problèmes similaires

Pour éviter des problèmes similaires à l'avenir :

1. **Standardisation des noms d'école** : Implémenter une validation des noms d'école pour éviter les variations orthographiques
2. **Vérification des types d'abonnement** : S'assurer que tous les utilisateurs d'une école ont le même type d'abonnement
3. **Simplification du code** : Utiliser uniquement `subscription_status == 'approved'` pour la détection des abonnements actifs
4. **Monitoring** : Ajouter des alertes pour détecter les incohérences dans les données d'abonnement

## Conclusion

Le problème de détection des écoles avec abonnement a été résolu avec succès en corrigeant à la fois le code et les données. Les enseignants peuvent maintenant s'associer correctement à leur école et accéder aux fonctionnalités de la plateforme sans redirection en boucle.
