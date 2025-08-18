# Correction du bouton "Souscrire un nouvel abonnement école"

## Problème initial

Le bouton "Souscrire un nouvel abonnement école" ne fonctionnait pas correctement pour les utilisateurs déjà connectés, notamment Sara. Les problèmes suivants ont été identifiés :

1. Lorsque Sara clique sur le bouton, aucune redirection visible ne se produit
2. Sara reçoit un message d'erreur lors de la création d'un compte école ("email existe déjà")
3. Le flux d'inscription et de souscription est bloqué

## Analyse technique

Après analyse approfondie, nous avons identifié les causes suivantes :

1. **Redirection incorrecte** : Sara, en tant qu'enseignante sans école ni abonnement, devrait être redirigée vers la page de sélection d'école (`payment.select_school`), mais cette redirection ne fonctionnait pas correctement.

2. **Type d'abonnement manquant** : Sara n'avait pas de type d'abonnement défini (`subscription_type: None`), ce qui pouvait causer des problèmes dans la logique de redirection.

3. **Flux d'inscription bloqué** : Le message d'erreur "email existe déjà" apparaît car Sara essaie de créer un nouveau compte alors qu'elle est déjà connectée.

## Solution implémentée

Nous avons créé un script de correction (`fix_school_subscription_simple.py`) qui :

1. **Corrige le type d'abonnement** : Définit `subscription_type='pending'` pour Sara si ce champ est vide.

2. **Ajoute une route de diagnostic** : `/fix/school-subscription` qui analyse l'état de l'utilisateur et applique les corrections nécessaires.

3. **Implémente une redirection correcte** : Redirige les enseignants sans abonnement approuvé vers la page de sélection d'école.

Le script d'intégration (`integrate_subscription_fix.py`) modifie `app.py` pour intégrer cette correction dans l'application Flask.

## Comment utiliser la solution

1. **Accéder à la page de diagnostic** : Visiter `/subscription-fix/school-subscription` lorsque vous êtes connecté en tant que Sara.

2. **Suivre le flux normal** : Après la correction, le bouton "Souscrire un nouvel abonnement école" redirigera correctement vers la page de sélection d'école.

## Vérification

Pour vérifier que la correction fonctionne :

1. Connectez-vous en tant que Sara (sara@gmail.com)
2. Accédez à la page de sélection d'école via `/subscription-fix/school-subscription`
3. Vérifiez que vous pouvez voir la liste des écoles avec abonnement actif
4. Sélectionnez une école ou souscrivez un nouvel abonnement école

## Déploiement

La correction a été intégrée dans l'application Flask et est prête à être déployée en production.
