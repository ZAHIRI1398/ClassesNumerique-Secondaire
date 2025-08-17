# Guide de vérification après déploiement

Ce guide vous explique comment vérifier que les modifications du flux d'abonnement ont été correctement déployées et fonctionnent comme prévu.

## 1. Exécuter le script de vérification des routes

Le script `check_routes_production.py` permet de vérifier automatiquement les routes et redirections en production.

### Étapes à suivre :

1. **Modifier le fichier `run_check_routes.bat`** :
   - Ouvrez le fichier `run_check_routes.bat` dans un éditeur de texte
   - Remplacez l'URL par celle de votre application en production :
     ```
     set PRODUCTION_APP_URL=https://votre-application.up.railway.app
     ```

2. **Exécuter le script** :
   - Double-cliquez sur `run_check_routes.bat`
   - Le script va vérifier toutes les routes importantes et afficher les résultats
   - Un fichier log sera également créé avec tous les détails

3. **Analyser les résultats** :
   - Vérifiez que la route `/payment/subscribe/school` redirige bien vers `/payment/select_school`
   - Vérifiez que la page `/payment/select_school` s'affiche correctement
   - Vérifiez qu'il n'y a pas de message "Aucune école avec un abonnement actif"

## 2. Vérifier les logs en production

Les logs en production contiennent des informations détaillées sur le flux d'abonnement.

### Logs à rechercher :

1. **Logs de la route `subscribe`** :
   ```
   [SUBSCRIBE_DEBUG] Accès à la route subscribe avec type=school
   [SUBSCRIBE_DEBUG] Utilisateur authentifié: True/False
   [SUBSCRIBE_DEBUG] Tentative de redirection vers /payment/select_school
   ```

2. **Logs de la route `select_school`** :
   ```
   [SELECT_SCHOOL_DEBUG] Accès à la route select_school
   [SELECT_SCHOOL_DEBUG] Méthode HTTP: GET
   [SELECT_SCHOOL_DEBUG] URL: /payment/select_school
   [SELECT_SCHOOL_DEBUG] Écoles avec abonnement actif: [...]
   ```

## 3. Tester manuellement le flux d'abonnement

Pour confirmer que tout fonctionne correctement, testez manuellement le flux d'abonnement.

### Étapes du test manuel :

1. Accédez à la page d'accueil de l'application
2. Cliquez sur "Abonnement" ou accédez à `/subscription-choice`
3. Sélectionnez l'option "École" ou accédez directement à `/payment/subscribe/school`
4. Vérifiez que vous êtes redirigé vers `/payment/select_school`
5. Vérifiez que la liste des écoles avec abonnement actif s'affiche correctement

## 4. Que faire en cas de problème

Si vous rencontrez des problèmes après le déploiement :

1. **Vérifiez les logs** pour identifier où se situe le problème
2. **Vérifiez que le Blueprint est correctement enregistré** dans `app.py`
3. **Vérifiez que les routes sont correctement définies** dans `payment_routes.py`
4. **Vérifiez que les écoles ont bien un abonnement actif** dans la base de données

En cas de problème persistant, vous pouvez utiliser le script `check_production_subscriptions.py` pour vérifier l'état des abonnements dans la base de données.
