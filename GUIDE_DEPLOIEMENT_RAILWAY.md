# Guide de déploiement manuel sur Railway

Ce guide explique comment déployer manuellement des modifications sur Railway après un push vers GitHub.

## Prérequis
- Accès au compte Railway
- Modifications déjà poussées vers GitHub

## Étapes de déploiement

### 1. Connexion à Railway
- Accédez à [Railway](https://railway.app/)
- Connectez-vous avec vos identifiants

### 2. Accès au projet
- Dans le tableau de bord, sélectionnez le projet "ClassesNumerique"
- Vous verrez la liste des services déployés (généralement un service web et une base de données PostgreSQL)

### 3. Déploiement manuel
- Sélectionnez le service web
- Cliquez sur l'onglet "Deployments" dans le menu latéral
- Cliquez sur le bouton "Deploy" ou "Redeploy" en haut à droite
- Sélectionnez la branche "main" comme source de déploiement
- Confirmez le déploiement

### 4. Suivi du déploiement
- Vous pouvez suivre l'avancement du déploiement dans l'onglet "Deployments"
- Le processus comprend généralement les étapes suivantes :
  - Clonage du dépôt
  - Installation des dépendances
  - Construction de l'application
  - Démarrage du service

### 5. Vérification du déploiement
- Une fois le déploiement terminé, cliquez sur l'URL générée pour accéder à l'application
- Vérifiez que les modifications sont bien appliquées
- Utilisez des scripts de vérification comme `verify_select_school_template.py` pour confirmer que tout fonctionne correctement

## Résolution des problèmes courants

### Erreur de déploiement
- Vérifiez les logs de déploiement pour identifier l'erreur
- Assurez-vous que toutes les dépendances sont correctement spécifiées dans `requirements.txt`
- Vérifiez que le `Procfile` est correctement configuré

### Application déployée mais non fonctionnelle
- Vérifiez les variables d'environnement dans les paramètres du projet
- Consultez les logs de l'application pour identifier les erreurs
- Assurez-vous que la base de données est correctement configurée

## Automatisation du déploiement

Pour éviter d'avoir à déployer manuellement à chaque push, vous pouvez configurer le déploiement automatique :

1. Dans les paramètres du projet Railway, accédez à l'onglet "Settings"
2. Activez l'option "Auto Deploy" pour le service web
3. Sélectionnez la branche "main" comme source de déploiement automatique

Avec cette configuration, chaque push vers la branche main sur GitHub déclenchera automatiquement un nouveau déploiement sur Railway.
