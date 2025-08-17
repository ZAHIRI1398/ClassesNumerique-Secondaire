# Documentation de la correction du problème de choix d'école

## Problème identifié

Le problème de choix d'école qui fonctionne en local mais pas en production est dû à deux facteurs principaux :

1. **Incohérence des types d'abonnement** : Certaines écoles ont des utilisateurs avec `subscription_type` = 'Trial' ou 'trial' au lieu de 'school'.

2. **Statuts d'abonnement non approuvés** : Des écoles ont des abonnements avec statut 'pending' ou 'paid' qui ne sont pas détectés par la fonctionnalité de choix d'école qui filtre uniquement sur le statut 'approved'.

## Analyse du code

Dans le fichier `payment_routes.py`, la route `/select_school` utilise la requête suivante pour trouver les écoles avec abonnement actif :

```python
schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
    filter(User.school_name != None).\
    filter(User.school_name != '').\
    filter(User.subscription_type.in_(['school', 'Trial', 'trial'])).\
    filter(User.subscription_status.in_(['pending', 'paid', 'approved'])).\
    group_by(User.school_name).all()
```

Cependant, lors de la vérification de l'abonnement d'une école spécifique, le code utilise :

```python
school_subscription = User.query.filter(
    User.school_name == school_name,
    User.subscription_type.in_(['school', 'Trial', 'trial']),
    User.subscription_status == 'approved'  # Uniquement 'approved', pas 'pending' ou 'paid'
).first()
```

Cette différence de filtrage crée une incohérence : des écoles peuvent apparaître dans la liste mais ne pas être considérées comme ayant un abonnement actif lors de la sélection.

## Solution implémentée

Nous avons créé deux scripts pour résoudre ce problème :

### 1. Script de diagnostic (`diagnostic_school_choice.py`)

Ce script crée une route `/diagnostic/school-choice` qui :
- Analyse tous les types et statuts d'abonnement dans la base de données
- Simule la requête de sélection d'école pour identifier les écoles éligibles
- Compare les différentes requêtes pour identifier les incohérences
- Fournit des informations détaillées pour le débogage

### 2. Script de correction (`fix_school_choice.py`)

Ce script crée une route `/fix/school-choice` qui :
- Convertit tous les abonnements 'Trial' et 'trial' en 'school' pour les utilisateurs associés à une école
- Met à jour les statuts 'pending' et 'paid' en 'approved' pour les abonnements de type 'school'
- Fournit un rapport détaillé des modifications effectuées

## Scripts d'intégration

Deux scripts d'intégration ont été créés pour faciliter l'ajout de ces fonctionnalités à l'application existante :

1. `integrate_diagnostic.py` : Intègre le blueprint de diagnostic dans `app.py`
2. `integrate_fix.py` : Intègre le blueprint de correction dans `app.py`

Ces scripts créent automatiquement une sauvegarde de `app.py` avant de le modifier.

## Instructions de déploiement

1. **Déploiement des scripts** :
   - Transférer les fichiers `diagnostic_school_choice.py`, `fix_school_choice.py`, `integrate_diagnostic.py` et `integrate_fix.py` sur le serveur de production.

2. **Intégration des blueprints** :
   ```bash
   python integrate_diagnostic.py
   python integrate_fix.py
   ```

3. **Redémarrage de l'application** :
   - Redémarrer l'application Flask pour prendre en compte les modifications.

4. **Diagnostic et correction** :
   - Accéder à `/diagnostic/school-choice` pour diagnostiquer le problème (nécessite des droits administrateur).
   - Accéder à `/fix/school-choice` pour appliquer la correction (nécessite des droits administrateur).

5. **Vérification** :
   - Après la correction, accéder à nouveau à `/diagnostic/school-choice` pour vérifier que le problème est résolu.
   - Tester la fonctionnalité de choix d'école en tant qu'enseignant.

## Résultat attendu

Après l'application de la correction :
- Tous les abonnements 'Trial' et 'trial' seront convertis en 'school'.
- Tous les statuts 'pending' et 'paid' pour les abonnements 'school' seront convertis en 'approved'.
- La fonctionnalité de choix d'école affichera correctement toutes les écoles éligibles.
- Les enseignants pourront s'associer à leur école sans problème.

## Prévention des problèmes futurs

Pour éviter que ce problème ne se reproduise à l'avenir :

1. **Uniformisation des types d'abonnement** : Utiliser uniquement 'school' comme type d'abonnement pour les écoles.
2. **Gestion cohérente des statuts** : S'assurer que les statuts sont correctement mis à jour lors des paiements.
3. **Filtrage cohérent** : Utiliser les mêmes critères de filtrage dans toutes les parties du code.
4. **Monitoring régulier** : Utiliser la route de diagnostic pour vérifier régulièrement l'état des abonnements.
