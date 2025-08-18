# Guide de déploiement des corrections d'affichage d'images

Ce guide détaille les étapes à suivre pour déployer les corrections d'affichage d'images dans l'environnement de production.

## Prérequis

- Accès à l'environnement de production (Railway)
- Droits d'administration sur la base de données
- Configuration Cloudinary correcte dans les variables d'environnement

## Étapes de déploiement

### 1. Sauvegarde préalable

```bash
# Créer une sauvegarde de la base de données
pg_dump -U username -h hostname -d database_name > backup_before_image_fix.sql

# Créer une sauvegarde des fichiers modifiés
cp app.py app.py.bak_image_fix
```

### 2. Déploiement des fichiers

Déployer les fichiers suivants sur le serveur de production:

- `fix_image_paths.py` - Module principal avec les routes de correction
- `integrate_image_sync.py` - Script d'intégration dans app.py
- `DOCUMENTATION_CORRECTION_AFFICHAGE_IMAGES_COMPLETE.md` - Documentation complète

### 3. Intégration dans l'application

```bash
# Exécuter le script d'intégration
python integrate_image_sync.py

# Vérifier que l'intégration a été effectuée correctement
grep -n "register_image_sync_routes" app.py
```

### 4. Redémarrage de l'application

```bash
# Redémarrer l'application Flask
touch wsgi.py  # Pour déclencher un redémarrage sur certains serveurs
# Ou utiliser la commande spécifique à votre environnement de déploiement
```

## Vérification post-déploiement

### 1. Vérifier l'accès aux routes

Accéder aux routes suivantes pour vérifier qu'elles fonctionnent correctement:

- `/fix-template-paths` - Correction des templates
- `/sync-image-paths` - Synchronisation des chemins d'images
- `/check-image-consistency` - Vérification de la cohérence
- `/create-simple-placeholders` - Création d'images placeholder

### 2. Ordre d'exécution recommandé

Pour une correction complète, exécuter les routes dans cet ordre:

1. **Correction des templates**: `/fix-template-paths`
   - Vérifie que tous les templates utilisent `cloud_storage.get_cloudinary_url`
   - Corrige automatiquement les templates problématiques

2. **Synchronisation des chemins**: `/sync-image-paths`
   - Met à jour `content.main_image` avec la valeur normalisée de `exercise.image_path`
   - Génère un rapport détaillé des modifications

3. **Vérification de la cohérence**: `/check-image-consistency`
   - Identifie les exercices avec des incohérences restantes
   - Permet de corriger individuellement chaque problème

4. **Création d'images placeholder**: `/create-simple-placeholders`
   - Crée des images SVG pour les images manquantes
   - Évite les erreurs 404 en production

### 3. Validation visuelle

Après avoir exécuté toutes les corrections:

1. Vérifier l'affichage des images dans différents types d'exercices:
   - Exercices de légende
   - Exercices de type QCM avec images
   - Exercices de type fill-in-blanks avec images
   - Exercices de type image-labeling

2. Tester la création d'un nouvel exercice avec upload d'image

3. Tester la modification d'un exercice existant avec changement d'image

## Résolution des problèmes courants

### Problème: Les images ne s'affichent toujours pas après correction

**Solution**: Vérifier les points suivants:
- Les variables d'environnement Cloudinary sont correctement configurées
- Le dossier `static/uploads` existe et a les permissions appropriées
- Les URLs des images sont correctement formées (utiliser l'inspecteur du navigateur)

### Problème: Erreurs lors de la synchronisation des chemins

**Solution**:
- Consulter les logs de l'application pour identifier les erreurs spécifiques
- Corriger manuellement les exercices problématiques via la route `/fix-single-exercise/<exercise_id>`

### Problème: Les templates ne sont pas correctement mis à jour

**Solution**:
- Vérifier que le script a les permissions nécessaires pour modifier les fichiers
- Mettre à jour manuellement les templates problématiques

## Surveillance et maintenance

### Surveillance à court terme

Après le déploiement, surveiller:
- Les logs de l'application pour détecter d'éventuelles erreurs
- Les performances de l'application (temps de chargement des pages)
- Les retours utilisateurs sur l'affichage des images

### Maintenance à long terme

Pour éviter que les problèmes ne réapparaissent:

1. **Exécuter régulièrement la vérification de cohérence**:
   ```bash
   # Ajouter une tâche cron pour vérifier la cohérence hebdomadaire
   0 0 * * 0 curl https://votre-domaine.com/check-image-consistency > /var/log/image-check.log
   ```

2. **Mettre à jour la documentation pour les développeurs**:
   - Documenter l'utilisation obligatoire de `cloud_storage.get_cloudinary_url`
   - Expliquer l'importance de la synchronisation entre `exercise.image_path` et `content.main_image`

3. **Ajouter des tests automatisés**:
   - Intégrer `test_image_display_fix.py` dans la suite de tests
   - Ajouter des tests d'intégration pour l'affichage des images

## Conclusion

Ce déploiement corrige les problèmes d'affichage des images en:
- Assurant la cohérence entre les différents champs de stockage d'images
- Normalisant tous les chemins d'images
- Corrigeant les templates pour utiliser la fonction appropriée
- Fournissant des images placeholder pour éviter les erreurs 404

Ces corrections garantissent un affichage fiable des images dans tous les types d'exercices, tant en développement qu'en production.
