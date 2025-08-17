# Guide de vérification du déploiement de la correction select-school

Ce guide détaille les étapes à suivre pour vérifier que la correction de la route `/payment/select-school` a été correctement déployée et fonctionne en production.

## 1. Vérification du déploiement

### 1.1 Vérifier le statut du déploiement sur Railway

- Connectez-vous à l'interface d'administration Railway
- Vérifiez que le dernier déploiement s'est terminé avec succès (statut "Deployed")
- Vérifiez les logs pour vous assurer qu'il n'y a pas d'erreurs au démarrage

### 1.2 Vérifier l'accès aux routes de diagnostic

- Connectez-vous à l'application en tant qu'administrateur
- Accédez à l'URL: `https://votre-domaine.up.railway.app/diagnose/select-school-route`
- Vérifiez que la page de diagnostic s'affiche correctement
- Si vous obtenez une erreur 404, cela signifie que les blueprints n'ont pas été correctement intégrés

## 2. Analyse du diagnostic

### 2.1 Vérifier le template

- Dans la page de diagnostic, vérifiez la section "Vérification du template"
- Assurez-vous que le template `payment/select_school.html` existe
- Si le template n'existe pas, vous devrez le créer manuellement

### 2.2 Vérifier les écoles avec abonnement

- Examinez la section "Écoles avec abonnement actif"
- Vérifiez qu'au moins une école apparaît dans la liste
- Pour chaque école, vérifiez les types et statuts d'abonnement
- Les écoles doivent avoir au moins un utilisateur avec:
  - `subscription_type` = 'school' (ou 'Trial'/'trial' qui sont maintenant acceptés)
  - `subscription_status` = 'approved'

### 2.3 Analyser les problèmes potentiels

- Examinez la section "Problèmes potentiels"
- Si des problèmes sont identifiés, notez-les pour les corriger ultérieurement

## 3. Test de la correction

### 3.1 Tester la route corrigée

- Accédez à l'URL: `https://votre-domaine.up.railway.app/fix-payment/select-school`
- Vérifiez que la page s'affiche correctement sans erreur 500
- Si vous êtes redirigé vers la page de paiement, cela signifie qu'aucune école avec abonnement actif n'a été trouvée

### 3.2 Tester l'association à une école

- Connectez-vous en tant qu'enseignant
- Accédez à la route corrigée: `/fix-payment/select-school`
- Sélectionnez une école dans la liste
- Cliquez sur le bouton "Rejoindre cette école"
- Vérifiez que vous êtes bien associé à l'école (message de confirmation)

## 4. Vérification finale

### 4.1 Tester la route originale

- Une fois que vous avez confirmé que la route corrigée fonctionne
- Accédez à l'URL originale: `https://votre-domaine.up.railway.app/payment/select-school`
- Vérifiez si l'erreur 500 persiste ou si la correction a résolu le problème

### 4.2 Vérifier les logs

- Consultez les logs de l'application dans Railway
- Recherchez les entrées avec les tags `[SELECT_SCHOOL_DEBUG]` ou `[FIX_SELECT_SCHOOL]`
- Vérifiez qu'il n'y a pas d'erreurs non traitées

## 5. Actions correctives supplémentaires

Si des problèmes persistent après le déploiement de la correction:

### 5.1 Problèmes de template

- Vérifiez que le template `payment/select_school.html` existe dans le répertoire `templates/payment/`
- Si nécessaire, créez-le manuellement en vous basant sur `fix_payment_select_school.html`

### 5.2 Problèmes d'abonnements

- Utilisez le script `fix_trial_subscriptions.py` pour corriger les types d'abonnement
- Exécutez: `python fix_trial_subscriptions.py --fix`

### 5.3 Problèmes d'intégration

- Vérifiez que les blueprints sont correctement enregistrés dans `app.py`
- Si nécessaire, ajoutez manuellement le code d'intégration:
  ```python
  from integrate_select_school_fix import integrate_select_school_fix
  integrate_select_school_fix(app)
  ```

## 6. Documentation des résultats

- Documentez les résultats de vos tests dans un fichier de suivi
- Notez les problèmes rencontrés et les solutions appliquées
- Conservez les logs pertinents pour référence future
