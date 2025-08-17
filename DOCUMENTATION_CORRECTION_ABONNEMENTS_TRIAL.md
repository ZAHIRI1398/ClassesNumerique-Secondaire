# Correction des abonnements de type 'Trial' et 'trial'

## Problème identifié

Lors de la vérification du flux d'abonnement école, nous avons constaté que certaines écoles n'étaient pas détectées correctement dans la liste des écoles avec abonnement actif. Après analyse, nous avons identifié que plusieurs écoles avaient un abonnement de type `Trial` ou `trial` au lieu de `school`, ce qui les excluait de la requête SQL qui filtrait uniquement sur le type `school`.

## Solution implémentée

### 1. Modification de `payment_routes.py`

Nous avons modifié trois parties du fichier `payment_routes.py` pour inclure les types d'abonnement `Trial` et `trial` :

#### a) Route `/payment/select_school`

```python
# AVANT
schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
    filter(User.school_name != None).\
    filter(User.school_name != '').\
    filter(User.subscription_type == 'school').\
    filter(User.subscription_status.in_(['pending', 'paid', 'approved'])).\
    group_by(User.school_name).all()

# APRÈS
schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
    filter(User.school_name != None).\
    filter(User.school_name != '').\
    filter(User.subscription_type.in_(['school', 'Trial', 'trial'])).\
    filter(User.subscription_status.in_(['pending', 'paid', 'approved'])).\
    group_by(User.school_name).all()
```

#### b) Route `/payment/join_school`

```python
# AVANT
school_subscription = User.query.filter(
    User.school_name == school_name,
    User.subscription_type == 'school',
    User.subscription_status == 'approved'
).first()

# APRÈS
school_subscription = User.query.filter(
    User.school_name == school_name,
    User.subscription_type.in_(['school', 'Trial', 'trial']),
    User.subscription_status == 'approved'
).first()
```

#### c) Route `/payment/subscribe/<subscription_type>`

```python
# AVANT
school_subscription = User.query.filter(
    User.school_name == current_user.school_name,
    User.subscription_type == 'school',
    User.subscription_status == 'approved'
).first()

# APRÈS
school_subscription = User.query.filter(
    User.school_name == current_user.school_name,
    User.subscription_type.in_(['school', 'Trial', 'trial']),
    User.subscription_status == 'approved'
).first()
```

### 2. Scripts de correction des données

Nous avons créé deux scripts pour corriger les données existantes :

#### a) `fix_trial_subscriptions.py`

Ce script permet de :
- Identifier tous les utilisateurs avec un abonnement de type `Trial` ou `trial`
- Identifier les écoles qui ont uniquement des abonnements de type `Trial` ou `trial`
- Corriger les types d'abonnement de `Trial`/`trial` vers `school`

#### b) `admin_fix_subscriptions.py`

Ce script ajoute un endpoint d'administration `/admin/fix/subscriptions` qui permet de :
- Corriger automatiquement les abonnements de type `Trial`/`trial` en `school`
- Afficher des statistiques sur les corrections effectuées
- Sécuriser l'accès avec authentification administrateur

### 3. Scripts batch pour l'exécution locale

- `run_fix_trial_subscriptions.bat` : Pour exécuter le script de correction des abonnements Trial
- `deploy_trial_fix.bat` : Pour déployer les modifications de code en production

## Comment vérifier le bon fonctionnement

1. **Vérifier les logs dans Railway** :
   - Rechercher les entrées avec le préfixe `[SELECT_SCHOOL_DEBUG]`
   - Vérifier que des écoles avec abonnement de type `Trial`/`trial` sont maintenant détectées

2. **Tester le flux d'abonnement** :
   - Se connecter en tant qu'enseignant
   - Accéder à `/payment/subscribe/school`
   - Vérifier que la redirection vers `/payment/select_school` fonctionne
   - Vérifier que les écoles avec abonnement `Trial`/`trial` sont affichées

3. **Exécuter le script de correction des données** :
   - Utiliser l'endpoint `/admin/fix/subscriptions` (nécessite des droits admin)
   - Ou exécuter le script `run_fix_trial_subscriptions.bat --fix` en local

## Impact des modifications

Ces modifications permettent de :
- Détecter correctement toutes les écoles avec abonnement, quel que soit le type (`school`, `Trial` ou `trial`)
- Éviter les redirections infinies pour les enseignants associés à des écoles avec abonnement `Trial`/`trial`
- Maintenir la compatibilité avec les données existantes tout en corrigeant progressivement les types d'abonnement

## Recommandations pour l'avenir

Pour éviter ce type de problème à l'avenir, nous recommandons de :
1. Standardiser les types d'abonnement dans l'interface d'administration
2. Ajouter des validations lors de la création/modification des abonnements
3. Mettre à jour régulièrement les abonnements de type `Trial`/`trial` vers `school`
