# Guide de vérification du déploiement des corrections d'affichage d'images

Ce guide vous aidera à vérifier que les corrections d'affichage d'images ont été correctement déployées sur Railway et fonctionnent comme prévu.

## 1. Vérification des routes de correction

Après le déploiement sur Railway, accédez aux routes suivantes dans l'ordre indiqué :

### a. Vérification de la cohérence des chemins d'images
```
https://votre-app.railway.app/check-image-consistency
```
Cette route affichera un rapport sur la cohérence entre `exercise.image_path` et `content.main_image`.

**Résultat attendu :** Liste des exercices avec des incohérences ou message confirmant que tout est cohérent.

### b. Synchronisation des chemins d'images
```
https://votre-app.railway.app/sync-image-paths
```
Cette route synchronisera les chemins d'images entre `exercise.image_path` et `content.main_image`.

**Résultat attendu :** Confirmation du nombre d'exercices synchronisés.

### c. Correction des templates
```
https://votre-app.railway.app/fix-template-paths
```
Cette route corrigera les templates qui n'utilisent pas `cloud_storage.get_cloudinary_url`.

**Résultat attendu :** Confirmation que les templates ont été corrigés.

### d. Création d'images placeholder
```
https://votre-app.railway.app/create-simple-placeholders
```
Cette route créera des images placeholder SVG pour les images manquantes.

**Résultat attendu :** Confirmation du nombre d'images placeholder créées.

## 2. Test d'affichage des images par type d'exercice

Vérifiez l'affichage des images dans chaque type d'exercice :

### QCM
1. Accédez à un exercice QCM avec image
2. Vérifiez que l'image s'affiche correctement
3. Inspectez le code source pour confirmer l'utilisation de `cloud_storage.get_cloudinary_url`

### Texte à trous (Fill in the blanks)
1. Accédez à un exercice de type "Texte à trous" avec image
2. Vérifiez que l'image s'affiche correctement
3. Confirmez que le chemin d'image ne contient pas de duplication `/static/uploads/static/uploads/`

### Légende (Legend)
1. Accédez à un exercice de type "Légende" avec image
2. Vérifiez que l'image principale s'affiche correctement
3. Confirmez que les zones et étiquettes sont correctement positionnées

### Autres types d'exercices
Répétez la vérification pour les autres types d'exercices disponibles :
- Souligner les mots
- Mots à placer
- QCM Multichoix
- Dictée
- Mots mêlés

## 3. Vérification des logs Railway

1. Accédez au dashboard Railway
2. Consultez les logs de l'application
3. Recherchez des erreurs liées à l'affichage des images ou à Cloudinary
4. Vérifiez que les routes de correction ont été exécutées sans erreur

## 4. Vérification de la configuration Cloudinary

1. Accédez à la route `/debug-cloudinary` (si disponible)
2. Vérifiez que les variables d'environnement Cloudinary sont correctement configurées :
   - CLOUDINARY_CLOUD_NAME
   - CLOUDINARY_API_KEY
   - CLOUDINARY_API_SECRET

## 5. Résolution des problèmes courants

### Images toujours manquantes
- Vérifiez que les variables Cloudinary sont correctement configurées
- Confirmez que les chemins d'images dans la base de données sont corrects
- Assurez-vous que les images existent dans votre compte Cloudinary

### Erreurs 404 sur les images
- Vérifiez les chemins d'images dans la console du navigateur
- Assurez-vous que les templates utilisent `cloud_storage.get_cloudinary_url`
- Vérifiez que les placeholders sont créés pour les images manquantes

### Erreurs 500
- Consultez les logs Railway pour identifier l'erreur précise
- Vérifiez que toutes les dépendances sont installées
- Assurez-vous que le blueprint a été correctement intégré

## 6. Confirmation finale

Une fois toutes les vérifications effectuées avec succès, vous pouvez confirmer que le déploiement des corrections d'affichage d'images est complet et fonctionnel.
