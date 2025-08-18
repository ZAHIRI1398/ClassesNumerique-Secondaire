# Guide de déploiement de la correction d'affichage d'images

Ce guide détaille les étapes à suivre pour déployer la solution de correction d'affichage d'images sur Railway.

## Mise à jour du 18 août 2025

### Dernières corrections apportées

La fonction `get_cloudinary_url` dans `cloud_storage.py` a été améliorée pour gérer correctement les cas spécifiques de chemins d'images dupliqués. Cette correction est essentielle pour résoudre les problèmes d'affichage d'images lors de la modification d'exercices.

**Principaux changements :**
- Traitement spécifique des chemins `/static/uploads/static/uploads/`
- Gestion améliorée des URL Cloudinary
- Logs de débogage détaillés
- Tests automatisés avec `test_image_path_handling.py`

## Étapes de déploiement

### 1. Préparation des fichiers

Assurez-vous que les fichiers suivants sont bien présents dans votre projet :

- `cloud_storage.py` : Module contenant la fonction `get_cloudinary_url` corrigée
- `fix_image_display.py` : Module contenant les routes de diagnostic et correction
- `app.py` : Application principale avec l'intégration des routes
- `requirements.txt` : Avec l'ajout de `Pillow==11.3.0` pour la génération d'images

### 2. Vérification des dépendances

Ajoutez Pillow à votre fichier requirements.txt s'il n'est pas déjà présent :

```
Pillow==11.3.0
```

### 3. Déploiement sur Railway

1. Sauvegardez la version actuelle de `cloud_storage.py` :
   ```bash
   cp cloud_storage.py cloud_storage.py.backup_$(date +%Y%m%d_%H%M%S)
   ```

2. Commitez vos modifications :
   ```bash
   git add cloud_storage.py fix_image_display.py app.py DOCUMENTATION_CORRECTION_AFFICHAGE_IMAGES.md GUIDE_DEPLOIEMENT_CORRECTION_IMAGES.md test_image_path_handling.py
   git commit -m "Fix: Correction de la fonction get_cloudinary_url pour les chemins d'images dupliqués"
   git push
   ```

3. Déployez sur Railway via votre méthode habituelle (GitHub integration ou CLI)

### 4. Vérification post-déploiement

Une fois le déploiement terminé, suivez ces étapes dans l'ordre :

1. **Vérifier les logs de la fonction `get_cloudinary_url`** :
   - Accédez au dashboard Railway et consultez les logs
   - Recherchez les entrées `[IMAGE_PATH_DEBUG]` pour vérifier le traitement des chemins
   - Assurez-vous qu'il n'y a pas d'erreurs lors du traitement des chemins dupliqués

2. **Tester la modification d'exercices avec images** :
   - Connectez-vous en tant qu'enseignant
   - Modifiez un exercice existant avec une image
   - Enregistrez et vérifiez que l'image s'affiche correctement après modification
   - Essayez de remplacer l'image et vérifiez à nouveau l'affichage

3. **Créer le répertoire manquant si nécessaire** :
   - Accédez à `https://votre-app.railway.app/fix-uploads-directory`
   - Vérifiez que la réponse indique `"success": true`

4. **Analyser les chemins d'images** :
   - Accédez à `https://votre-app.railway.app/check-image-paths`
   - Examinez le rapport pour identifier les images manquantes ou les chemins problématiques

5. **Générer les images placeholder si nécessaire** :
   - Accédez à `https://votre-app.railway.app/create-placeholder-images`
   - Vérifiez que des images ont été créées pour les chemins manquants

6. **Vérifier les exercices dans différents templates** :
   - Naviguez vers des exercices utilisant différents templates (fill_in_blanks, qcm, etc.)
   - Confirmez que les images s'affichent correctement dans tous les contextes

## Résolution des problèmes courants

### Images toujours manquantes après déploiement

Si certaines images sont toujours manquantes après avoir suivi les étapes ci-dessus :

1. **Vérifiez les logs Railway** :
   ```bash
   railway logs
   ```
   Recherchez des erreurs liées à la création du répertoire ou des images

2. **Vérifiez les permissions** :
   - Railway peut avoir des restrictions sur la création de fichiers
   - Essayez de modifier les permissions du répertoire static

3. **Solution alternative** :
   - Uploadez manuellement les images manquantes via le dashboard Railway
   - Ou utilisez la fonctionnalité de volumes persistants de Railway

### Erreurs lors de la génération d'images placeholder

Si vous rencontrez des erreurs lors de la génération d'images :

1. **Vérifiez l'installation de Pillow** :
   - Confirmez que Pillow est bien installé dans l'environnement Railway
   - Vérifiez la version dans les logs de déploiement

2. **Problèmes de mémoire** :
   - Réduisez la taille des images générées si nécessaire
   - Limitez le nombre d'images générées en une seule requête

## Test de la fonction get_cloudinary_url

Pour vérifier le bon fonctionnement de la fonction `get_cloudinary_url` corrigée, vous pouvez utiliser le script de test automatisé :

1. **Exécuter le script de test** :
   ```bash
   python test_image_path_handling.py
   ```

2. **Analyser les résultats** :
   - Vérifiez que tous les tests passent avec succès
   - Portez une attention particulière au test 3 (chemins dupliqués)
   - Examinez les logs pour comprendre le traitement des différents types de chemins

3. **Tests manuels complémentaires** :
   - Créez un exercice avec une image
   - Modifiez-le plusieurs fois en changeant l'image
   - Vérifiez dans les logs le traitement des chemins
   - Confirmez que l'image s'affiche correctement après chaque modification

## Maintenance à long terme

Pour une solution plus pérenne :

1. **Migration vers Cloudinary** :
   - Envisagez de migrer toutes les images vers Cloudinary
   - Créez un script de migration automatique
   - Utilisez la fonction `get_cloudinary_url` corrigée pour gérer les deux types de chemins

2. **Surveillance des erreurs** :
   - Mettez en place une surveillance des erreurs 404 sur les ressources statiques
   - Configurez des alertes en cas de problèmes d'affichage
   - Analysez régulièrement les logs `[IMAGE_PATH_DEBUG]`

3. **Backup régulier** :
   - Sauvegardez régulièrement le répertoire `static/uploads`
   - Ou utilisez un système de stockage persistant
