# Synchronisation des chemins d'images pour les exercices image_labeling

## Problème identifié

Après avoir corrigé le template d'affichage des exercices image_labeling, nous avons constaté que les images ne s'affichaient toujours pas correctement. Une analyse approfondie a révélé que pour la plupart des exercices de type image_labeling, le champ `exercise.image_path` était `NULL` dans la base de données, alors que le champ `content.main_image` contenait bien un chemin d'image valide.

### Cause racine

Le problème venait d'une incohérence dans la base de données :

1. **Champ `image_path` non renseigné** : Lors de la création d'exercices de type image_labeling, le champ `image_path` de la table `exercise` n'était pas correctement renseigné.

2. **Utilisation de `content.main_image` uniquement** : Le code de création des exercices sauvegardait correctement le chemin de l'image dans le champ JSON `content.main_image`, mais ne mettait pas à jour le champ `exercise.image_path`.

3. **Template modifié pour utiliser `content.main_image`** : Notre correction précédente du template a fait en sorte qu'il utilise directement `content.main_image`, mais certaines parties de l'application peuvent encore dépendre de `exercise.image_path`.

## Solution implémentée

Nous avons créé un script (`sync_image_paths.py`) pour synchroniser les chemins d'images entre `exercise.image_path` et `content.main_image` pour tous les exercices de type image_labeling :

1. **Analyse des exercices** : Le script identifie tous les exercices de type image_labeling dans la base de données.

2. **Détection des incohérences** : Pour chaque exercice, il compare les valeurs de `exercise.image_path` et `content.main_image`.

3. **Synchronisation** : Si `exercise.image_path` est `NULL` ou différent de `content.main_image`, il met à jour `exercise.image_path` avec la valeur de `content.main_image`.

4. **Sauvegarde de sécurité** : Avant toute modification, le script crée une sauvegarde de la base de données.

## Résultats

L'exécution du script a permis de :

- ✅ Analyser 5 exercices de type image_labeling
- ✅ Mettre à jour 4 exercices où `exercise.image_path` était `NULL` ou incohérent
- ✅ Confirmer que 1 exercice avait déjà des chemins synchronisés

## Correction du code de création

Pour éviter que ce problème ne se reproduise à l'avenir, il est recommandé de modifier le code de création des exercices de type image_labeling pour s'assurer que `exercise.image_path` est toujours correctement renseigné avec la même valeur que `content.main_image`.

## Recommandations pour l'avenir

1. **Cohérence des données** : Toujours maintenir une cohérence entre `exercise.image_path` et `content.main_image` pour les exercices qui utilisent des images.

2. **Validation des données** : Implémenter des validations pour s'assurer que les chemins d'images sont correctement renseignés lors de la création et de la modification des exercices.

3. **Normalisation des chemins** : Continuer à utiliser des chemins normalisés commençant par `/static/` pour toutes les ressources statiques.

4. **Vérifications périodiques** : Exécuter périodiquement des scripts de vérification pour détecter et corriger les incohérences dans la base de données.

## Fichiers concernés

- `sync_image_paths.py` : Script de synchronisation des chemins d'images
- Base de données SQLite : Mise à jour des champs `exercise.image_path` pour les exercices de type image_labeling
