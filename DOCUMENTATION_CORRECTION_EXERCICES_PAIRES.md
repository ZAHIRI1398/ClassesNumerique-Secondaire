# Documentation : Correction des exercices d'association de paires

## Problème initial

Les images dans les exercices d'association de paires ne s'affichaient pas correctement pour les raisons suivantes :

1. **Format de données incohérent** : Certains éléments étaient stockés comme simples chaînes de caractères au lieu d'objets avec `type` et `content`
2. **Chemins d'images incorrects** : Utilisation de `/static/exercises/` au lieu de `/static/uploads/`
3. **Structure JSON incompatible** : Le template `pairs.html` attendait un format spécifique que certains exercices ne respectaient pas

## Solution implémentée

Un script de correction automatique (`fix_pairs_image_display_complete.py`) a été créé pour :

1. **Normaliser les chemins d'images** : Conversion de tous les chemins vers le format `/static/uploads/`
2. **Convertir les éléments texte** : Transformation des chaînes simples en objets `{"type": "text", "content": "texte"}`
3. **Convertir les éléments image** : Transformation des chemins d'images en objets `{"type": "image", "content": "/chemin/image.png"}`
4. **Créer des sauvegardes** : Avant toute modification, une sauvegarde de l'exercice est créée
5. **Vérifier l'existence des images** : Création d'images placeholder si nécessaire

## Structure correcte des exercices de paires

Les exercices d'association de paires doivent suivre l'une des deux structures suivantes :

### Format 1 : Listes séparées

```json
{
  "left_items": [
    {"type": "text", "content": "Texte à gauche 1"},
    {"type": "image", "content": "/static/uploads/image1.png"}
  ],
  "right_items": [
    {"type": "text", "content": "Texte à droite 1"},
    {"type": "image", "content": "/static/uploads/image2.png"}
  ]
}
```

### Format 2 : Liste de paires

```json
{
  "pairs": [
    {
      "left": {"type": "text", "content": "Texte à gauche 1"},
      "right": {"type": "text", "content": "Texte à droite 1"}
    },
    {
      "left": {"type": "image", "content": "/static/uploads/image1.png"},
      "right": {"type": "image", "content": "/static/uploads/image2.png"}
    }
  ]
}
```

## Bonnes pratiques pour les exercices de paires

1. **Toujours utiliser des objets avec type/content** :
   - Pour le texte : `{"type": "text", "content": "Texte"}`
   - Pour les images : `{"type": "image", "content": "/static/uploads/image.png"}`

2. **Chemins d'images standardisés** :
   - Toujours utiliser le préfixe `/static/uploads/`
   - Éviter les caractères spéciaux dans les noms de fichiers
   - Utiliser des noms de fichiers uniques (timestamp ou UUID)

3. **Validation des données** :
   - Vérifier que chaque élément est un objet avec `type` et `content`
   - Vérifier que les images référencées existent physiquement
   - Valider la structure JSON avant sauvegarde

4. **Création d'exercices** :
   - Utiliser l'interface d'administration pour créer des exercices
   - Vérifier l'aperçu avant de sauvegarder
   - Tester l'affichage après création

## Comment utiliser le script de correction

Le script `fix_pairs_image_display_complete.py` peut être utilisé de plusieurs façons :

1. **Corriger tous les exercices** :
   ```
   python fix_pairs_image_display_complete.py --fix-all
   ```

2. **Corriger un exercice spécifique** :
   ```
   python fix_pairs_image_display_complete.py --fix-exercise-id 32
   ```

3. **Créer un exercice de test** :
   ```
   python fix_pairs_image_display_complete.py --create-test
   ```

## Fonctionnement du template pairs.html

Le template `pairs.html` attend des éléments avec la structure suivante :

```html
{% if item.type == 'image' %}
    <img src="{{ cloud_storage.get_cloudinary_url(item.content) }}" alt="Image" style="max-width: 100px; max-height: 100px; object-fit: contain;">
{% else %}
    <span class="pair-text">{{ item.content if item.content else item }}</span>
{% endif %}
```

Pour que les images s'affichent correctement :
1. L'élément doit avoir un attribut `type` égal à `'image'`
2. L'élément doit avoir un attribut `content` contenant le chemin de l'image
3. Le chemin doit être valide et l'image doit exister

## Intégration dans le workflow de création et d'édition

La fonction `normalize_pairs_exercise_content()` a été intégrée directement dans le workflow de création et d'édition des exercices de type "pairs" pour assurer une normalisation automatique des chemins d'images :

1. **Dans modified_submit.py** :
   - Import de la fonction depuis `normalize_pairs_exercise_paths.py`
   - Appel de la fonction juste après la construction du contenu des paires
   - Normalisation avant la sauvegarde en base de données

2. **Dans app.py (route d'édition)** :
   - Import de la fonction depuis `normalize_pairs_exercise_paths.py`
   - Appel de la fonction juste après la construction du contenu des paires
   - Normalisation avant la sauvegarde des modifications

Cette intégration assure que tous les nouveaux exercices créés et tous les exercices modifiés auront automatiquement leurs chemins d'images normalisés, sans nécessiter d'intervention manuelle ou de script de correction après coup.

## Maintenance future

Pour éviter les problèmes similaires à l'avenir :

1. **Validation des données** : Ajouter une validation côté serveur lors de la création/modification d'exercices
2. **Tests automatisés** : Créer des tests pour vérifier l'affichage des exercices
3. **Normalisation des chemins** : Utiliser une fonction helper pour normaliser les chemins d'images (déjà implémenté)
4. **Documentation** : Maintenir cette documentation à jour avec les changements futurs

## Conclusion

La correction des exercices d'association de paires a été réalisée en deux phases :

1. **Phase corrective** : Un script de correction a été créé pour normaliser les chemins d'images et convertir les éléments au format attendu dans les exercices existants.

2. **Phase préventive** : La fonction `normalize_pairs_exercise_content()` a été intégrée directement dans le workflow de création et d'édition des exercices pour assurer une normalisation automatique des chemins d'images.

Grâce à ces améliorations, tous les exercices de type "pairs" (existants et futurs) s'afficheront correctement dans l'interface utilisateur, sans nécessiter d'intervention manuelle ou de correction après coup. Cette approche proactive évite les problèmes d'affichage et améliore l'expérience utilisateur pour les enseignants et les élèves.
