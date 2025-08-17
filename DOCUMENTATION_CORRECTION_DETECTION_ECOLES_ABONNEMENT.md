# Correction de la détection des écoles avec abonnement

## Problème identifié

Un problème a été identifié dans la détection des écoles ayant un abonnement actif. Spécifiquement, l'école "École Bruxelles II" apparaissait comme ayant un abonnement actif dans l'interface utilisateur, mais n'était pas détectée correctement par le système lors de la sélection d'une école.

## Causes du problème

Après analyse, deux problèmes distincts ont été identifiés :

1. **Incohérence dans le nom de l'école** : Le nom de l'école était stocké dans la base de données comme "Ecole Bruxelles ll" (sans accent sur 'École' et avec des 'l' minuscules au lieu du chiffre romain 'II'), alors qu'il apparaissait comme "École Bruxelles II" dans l'interface utilisateur.

2. **Type d'abonnement incorrect** : L'utilisateur associé à l'école avait un type d'abonnement défini comme 'trial' au lieu de 'school', ce qui empêchait la détection correcte par la requête SQL qui filtre sur `subscription_type == 'school'`.

## Solutions mises en œuvre

### 1. Correction du nom de l'école

Un script a été créé pour mettre à jour le nom de l'école dans la base de données :

```python
# Rechercher les utilisateurs avec l'ancien nom d'école
old_name = "Ecole Bruxelles ll"
new_name = "École Bruxelles II"

users = User.query.filter_by(school_name=old_name).all()

# Mettre à jour le nom de l'école
for user in users:
    user.school_name = new_name

# Sauvegarder les modifications
db.session.commit()
```

### 2. Correction du type d'abonnement

Un script a été créé pour vérifier et corriger le type d'abonnement :

```python
# Rechercher l'utilisateur de l'École Bruxelles II
school_name = "École Bruxelles II"
user = User.query.filter_by(school_name=school_name).first()

# Corriger le type d'abonnement
if user.subscription_type != 'school':
    user.subscription_type = 'school'
    user.subscription_amount = 80.0  # Montant pour les écoles
    db.session.commit()
```

## Vérification et tests

Après avoir appliqué ces corrections, nous avons vérifié que l'école est maintenant correctement détectée comme ayant un abonnement actif :

```python
# Trouver toutes les écoles avec au moins un utilisateur ayant un abonnement actif
schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
    filter(User.school_name != None).\
    filter(User.school_name != '').\
    filter(User.subscription_type == 'school').\
    filter(User.subscription_status == 'approved').\
    group_by(User.school_name).all()

# Résultat : [('École Bruxelles II', 1)]
```

## Recommandations pour éviter ce problème à l'avenir

1. **Normalisation des noms d'écoles** : Mettre en place une validation ou normalisation des noms d'écoles lors de leur saisie pour éviter les incohérences (accents, majuscules, etc.).

2. **Vérification du type d'abonnement** : S'assurer que le type d'abonnement est correctement défini lors de la création ou de la modification d'un abonnement école.

3. **Interface d'administration** : Créer une interface d'administration pour gérer facilement les abonnements et les noms d'écoles.

4. **Tests automatisés** : Mettre en place des tests automatisés pour vérifier régulièrement la cohérence des données d'abonnement et de noms d'écoles.

## Scripts créés

Trois scripts ont été créés pour diagnostiquer et résoudre ce problème :

1. `update_school_name.py` : Met à jour le nom de l'école dans la base de données.
2. `check_user_subscription.py` : Vérifie et corrige le type d'abonnement de l'utilisateur.
3. `test_school_detection.py` : Teste la détection des écoles avec abonnement actif.

Ces scripts peuvent être utilisés comme référence pour résoudre des problèmes similaires à l'avenir.
