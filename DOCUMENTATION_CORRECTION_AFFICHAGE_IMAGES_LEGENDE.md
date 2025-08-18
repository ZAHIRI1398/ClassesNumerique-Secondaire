# Correction de l'affichage des images dans les exercices de type légende

## Problème initial

- Les images ne s'affichaient pas correctement dans les exercices de type légende
- Incohérence entre le stockage de l'image dans `exercise.image_path` et dans le contenu JSON (`main_image`)
- Le template `legend_edit.html` n'affichait que les images stockées dans le contenu JSON (`main_image`)
- Pas de synchronisation entre `exercise.image_path` et `main_image` dans le contenu JSON

## Causes identifiées

1. **Incohérence de stockage** : 
   - Les autres types d'exercices utilisent `exercise.image_path`
   - Les exercices de type légende utilisent `content.main_image` (stocké dans le JSON)

2. **Template incomplet** :
   - Le template `legend_edit.html` ne vérifiait pas `exercise.image_path` comme fallback
   - Seul `exercise.get_content().get('main_image')` était utilisé

3. **Synchronisation manquante** :
   - Lors de l'upload d'une image via `legend_main_image`, aucune synchronisation avec `exercise.image_path`
   - Lors de l'édition, l'image pouvait être présente dans un champ mais pas dans l'autre

## Solution implémentée

### 1. Correction du template `legend_edit.html`

- Ajout de la vérification de `exercise.image_path` comme fallback
- Amélioration du style des images (classes Bootstrap cohérentes)
- Affichage conditionnel selon la source de l'image

```html
<!-- Avant -->
{% if exercise.get_content().get('main_image') %}
<img src="{{ cloud_storage.get_cloudinary_url(exercise.get_content().get('main_image')) }}" alt="Image actuelle" style="max-width: 200px; max-height: 200px;">
{% endif %}

<!-- Après -->
{% if exercise.get_content().get('main_image') %}
<img src="{{ cloud_storage.get_cloudinary_url(exercise.get_content().get('main_image')) }}" alt="Image actuelle" class="img-fluid rounded shadow" style="max-width: 300px; max-height: 200px;">
{% endif %}
{% if exercise.image_path and not exercise.get_content().get('main_image') %}
<div class="mt-2">
    <p>Image de l'exercice:</p>
    <img src="{{ cloud_storage.get_cloudinary_url(exercise.image_path) }}" alt="Image de l'exercice" class="img-fluid rounded shadow" style="max-width: 300px; max-height: 200px;">
</div>
{% endif %}
```

### 2. Synchronisation bidirectionnelle dans `app.py`

- Lors de l'upload d'une nouvelle image via `legend_main_image`, mise à jour de `exercise.image_path`
- Utilisation de `exercise.image_path` comme fallback si `main_image_path` est vide
- Synchronisation finale pour garantir la cohérence des données

```python
# Lors de l'upload d'une nouvelle image
if 'legend_main_image' in request.files:
    image_file = request.files['legend_main_image']
    if image_file and image_file.filename != '' and allowed_file(image_file.filename):
        main_image_path = cloud_storage.upload_file(image_file, folder="legend")
        if main_image_path:
            # Synchroniser avec exercise.image_path pour assurer la cohérence
            exercise.image_path = main_image_path
            current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Image principale uploadée et synchronisée: {main_image_path}')

# Si pas d'image principale mais qu'il y a exercise.image_path, l'utiliser
if not main_image_path and exercise.image_path:
    main_image_path = exercise.image_path
    current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Utilisation de exercise.image_path comme image principale: {main_image_path}')

# Synchronisation finale après sauvegarde du contenu
if main_image_path and (not exercise.image_path or exercise.image_path != main_image_path):
    exercise.image_path = main_image_path
    current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Image path synchronisé: {exercise.image_path}')
```

## Résultat final

- ✅ Affichage cohérent des images dans tous les types d'exercices
- ✅ Synchronisation bidirectionnelle entre `exercise.image_path` et `main_image`
- ✅ Fallback automatique si l'image est présente dans un champ mais pas dans l'autre
- ✅ Logs de debug pour traçabilité des opérations sur les images
- ✅ Interface utilisateur améliorée avec styles cohérents

## Fichiers modifiés

- `templates/exercise_types/legend_edit.html` : Correction de l'affichage des images
- `app.py` : Ajout de la synchronisation bidirectionnelle des chemins d'images

## Impact

Les enseignants peuvent maintenant modifier les exercices de type légende avec des images qui s'affichent correctement, quelle que soit la façon dont elles ont été ajoutées initialement (via l'interface générale d'édition d'exercice ou via l'interface spécifique aux légendes).
