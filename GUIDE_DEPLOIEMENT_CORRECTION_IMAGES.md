# Guide de déploiement de la correction d'affichage d'images

Ce guide détaille les étapes à suivre pour déployer la solution de correction d'affichage d'images sur Railway.

## Étapes de déploiement

### 1. Préparation des fichiers

Assurez-vous que les fichiers suivants sont bien présents dans votre projet :

- `fix_image_display.py` : Module contenant les routes de diagnostic et correction
- `app.py` : Application principale avec l'intégration des routes
- `requirements.txt` : Avec l'ajout de `Pillow==11.3.0` pour la génération d'images

### 2. Vérification des dépendances

Ajoutez Pillow à votre fichier requirements.txt s'il n'est pas déjà présent :

```
Pillow==11.3.0
```

### 3. Déploiement sur Railway

1. Commitez vos modifications :
   ```bash
   git add fix_image_display.py app.py DOCUMENTATION_CORRECTION_AFFICHAGE_IMAGES_PRODUCTION.md
   git commit -m "Ajout des routes de diagnostic et correction d'images"
   git push
   ```

2. Déployez sur Railway via votre méthode habituelle (GitHub integration ou CLI)

### 4. Vérification post-déploiement

Une fois le déploiement terminé, suivez ces étapes dans l'ordre :

1. **Créer le répertoire manquant** :
   - Accédez à `https://votre-app.railway.app/fix-uploads-directory`
   - Vérifiez que la réponse indique `"success": true`

2. **Analyser les chemins d'images** :
   - Accédez à `https://votre-app.railway.app/check-image-paths`
   - Examinez le rapport pour identifier les images manquantes

3. **Générer les images placeholder** :
   - Accédez à `https://votre-app.railway.app/create-placeholder-images`
   - Vérifiez que des images ont été créées pour les chemins manquants

4. **Vérifier les exercices** :
   - Naviguez vers quelques exercices avec images pour confirmer qu'elles s'affichent correctement

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

## Maintenance à long terme

Pour une solution plus pérenne :

1. **Migration vers Cloudinary** :
   - Envisagez de migrer toutes les images vers Cloudinary
   - Créez un script de migration automatique

2. **Surveillance des erreurs** :
   - Mettez en place une surveillance des erreurs 404 sur les ressources statiques
   - Configurez des alertes en cas de problèmes d'affichage

3. **Backup régulier** :
   - Sauvegardez régulièrement le répertoire `static/uploads`
   - Ou utilisez un système de stockage persistant
