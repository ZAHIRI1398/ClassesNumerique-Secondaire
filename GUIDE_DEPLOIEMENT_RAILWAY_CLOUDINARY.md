# Guide de déploiement des corrections d'affichage d'images sur Railway

## Prérequis
- Accès au dashboard Railway
- Accès au compte Cloudinary
- Modifications déjà poussées sur GitHub

## 1. Configuration des variables d'environnement Cloudinary sur Railway

1. **Connectez-vous à votre dashboard Railway**
   - Accédez à [https://railway.app/dashboard](https://railway.app/dashboard)
   - Sélectionnez votre projet ClassesNumerique-Secondaire

2. **Accédez aux variables d'environnement**
   - Dans le menu de gauche, cliquez sur "Variables"
   - Ou cliquez sur l'onglet "Variables" dans la vue du projet

3. **Ajoutez les variables Cloudinary**
   - Cliquez sur "New Variable"
   - Ajoutez les trois variables suivantes:
     ```
     CLOUDINARY_CLOUD_NAME=votre_cloud_name
     CLOUDINARY_API_KEY=votre_api_key
     CLOUDINARY_API_SECRET=votre_api_secret
     ```
   - Remplacez les valeurs par celles de votre compte Cloudinary
   - Cliquez sur "Add" pour chaque variable

4. **Vérifiez les variables**
   - Assurez-vous que les trois variables sont bien présentes
   - Vérifiez l'orthographe exacte des noms de variables

## 2. Déploiement via GitHub

1. **Exécutez le script de déploiement**
   - Double-cliquez sur `deploy_image_fix_github.bat`
   - Ou ouvrez un terminal et exécutez:
     ```
     cd c:\Users\JeMat\OneDrive\classenumerique20250801
     deploy_image_fix_github.bat
     ```
   - Suivez les instructions à l'écran

2. **Vérifiez le push GitHub**
   - Assurez-vous que le message de succès s'affiche
   - Vérifiez sur GitHub que les modifications sont bien présentes

3. **Déclenchez un déploiement sur Railway**
   - Retournez sur votre dashboard Railway
   - Sélectionnez votre projet
   - Cliquez sur "Deployments" dans le menu de gauche
   - Cliquez sur "Deploy now" ou "Redeploy"
   - Attendez que le déploiement soit terminé (statut "Success")

## 3. Vérification et activation des corrections

Une fois le déploiement terminé, accédez aux routes suivantes pour activer les corrections:

1. **Vérification de la cohérence des chemins d'images**
   - Accédez à `https://votre-app.railway.app/check-image-consistency`
   - Vérifiez les résultats affichés

2. **Synchronisation des chemins d'images**
   - Accédez à `https://votre-app.railway.app/sync-image-paths`
   - Cette route synchronise `exercise.image_path` et `content.main_image`

3. **Correction des templates**
   - Accédez à `https://votre-app.railway.app/fix-template-paths`
   - Cette route corrige les templates qui n'utilisent pas `cloud_storage.get_cloudinary_url`

4. **Création d'images placeholder**
   - Accédez à `https://votre-app.railway.app/create-simple-placeholders`
   - Cette route crée des images placeholder SVG pour les images manquantes

## 4. Vérification finale

1. **Testez l'affichage des exercices**
   - Connectez-vous en tant qu'enseignant ou élève
   - Accédez à différents types d'exercices
   - Vérifiez que les images s'affichent correctement

2. **Vérifiez les logs**
   - Dans le dashboard Railway, cliquez sur "Logs"
   - Recherchez d'éventuelles erreurs liées aux images
   - Vérifiez que les routes de correction ont bien été exécutées

## Résolution de problèmes

Si vous rencontrez des problèmes:

1. **Images toujours manquantes**
   - Vérifiez que les variables Cloudinary sont correctes
   - Accédez à `/debug-cloudinary` pour tester la configuration

2. **Erreurs 500**
   - Vérifiez les logs Railway pour identifier l'erreur
   - Assurez-vous que le blueprint a bien été intégré dans app.py

3. **Problèmes de déploiement**
   - Vérifiez que tous les fichiers nécessaires ont été poussés
   - Assurez-vous que le déploiement est bien terminé (statut "Success")

## Support

En cas de problème persistant, consultez la documentation complète:
- `DOCUMENTATION_CORRECTION_AFFICHAGE_IMAGES_COMPLETE.md`
- `GUIDE_DEPLOIEMENT_CORRECTION_IMAGES_COMPLET.md`
