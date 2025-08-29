# Documentation de la correction d'affichage des images lors de l'édition d'exercices

## Problèmes identifiés

### Problème 1 : Incohérence des chemins d'images

Lors de l'édition d'exercices, les images ne s'affichaient pas correctement en raison d'une incohérence dans le stockage des chemins d'images entre deux emplacements :

1. `exercise.image_path` : Attribut direct de l'objet Exercise dans la base de données
2. `content['image']` ou `content['main_image']` : Chemin stocké dans le contenu JSON de l'exercice

Le problème venait du fait que la route d'édition d'exercice (`/exercise/<int:exercise_id>/edit`) stockait parfois l'image uniquement dans le contenu JSON et mettait `exercise.image_path` à `None`, alors que les templates utilisent principalement `exercise.image_path` pour afficher l'image.

### Problème 2 : Erreur "name 'cloud_storage' is not defined"

Les templates de modification d'exercice (`edit_exercise.html` et `test_edit_exercise.html`) utilisaient directement `exercise.image_path` comme source de l'image, sans passer par la fonction `cloud_storage.get_cloudinary_url()`. Cela causait deux problèmes :

1. Les images ne s'affichaient pas correctement car les chemins n'étaient pas normalisés
2. Lorsque les templates ont été modifiés pour utiliser `cloud_storage.get_cloudinary_url()`, l'erreur "name 'cloud_storage' is not defined" apparaissait car la variable `cloud_storage` n'était pas disponible dans le contexte du template

## Solution implémentée

### 1. Modification de la route d'édition d'exercice

La route d'édition d'exercice a été modifiée pour maintenir la cohérence entre `exercise.image_path` et `content['image']` :

- Lors de l'upload d'une nouvelle image, le chemin est désormais stocké à la fois dans `exercise.image_path` et dans `content['image']`
- Lors de la suppression d'une image, les deux emplacements sont mis à jour
- Une logique de synchronisation a été ajoutée pour s'assurer que les deux emplacements contiennent toujours la même valeur

### 2. Correction des templates de modification d'exercice

Les templates de modification d'exercice ont été mis à jour pour utiliser `cloud_storage.get_cloudinary_url()` au lieu d'accéder directement à `exercise.image_path` :

#### Template `edit_exercise.html` :

```html
<!-- Avant la correction -->
<img src="{{ exercise.image_path }}" 
     alt="Image de l'exercice" 
     onerror="this.style.display='none';"
     style="max-width: 300px; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

<!-- Après la correction -->
<img src="{{ cloud_storage.get_cloudinary_url(exercise.image_path) }}" 
     alt="Image de l'exercice" 
     onerror="this.style.display='none';"
     style="max-width: 300px; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
```

#### Template `test_edit_exercise.html` :

```html
<!-- Avant la correction -->
{% if exercise.image_path %}
    <img src="{{ exercise.image_path }}" alt="Image actuelle">
{% elif content.image %}
    <img src="{{ content.image }}" alt="Image actuelle">
{% else %}
    <div class="text-center p-4 bg-light">
        <em>Pas d'image</em>
    </div>
{% endif %}

<!-- Après la correction -->
{% if exercise.image_path %}
    <img src="{{ cloud_storage.get_cloudinary_url(exercise.image_path) }}" alt="Image actuelle">
{% elif content.image %}
    <img src="{{ cloud_storage.get_cloudinary_url(content.image) }}" alt="Image actuelle">
{% else %}
    <div class="text-center p-4 bg-light">
        <em>Pas d'image</em>
    </div>
{% endif %}
```

### 3. Ajout d'une route de synchronisation

Une nouvelle route `/fix-edit-image-display` a été ajoutée dans le blueprint `image_sync_bp` pour corriger les incohérences existantes dans la base de données. Cette route :

- Analyse tous les exercices dans la base de données
- Vérifie la cohérence entre `exercise.image_path` et `content['image']`
- Synchronise les valeurs en cas d'incohérence
- Génère un rapport HTML des modifications effectuées

### 4. Injection du service cloud_storage dans les templates

Pour résoudre l'erreur "name 'cloud_storage' is not defined", nous avons vérifié que le service `cloud_storage` est bien injecté dans tous les templates via la fonction `inject_cloud_storage()` dans `app.py` :

```python
# Dans app.py
@app.context_processor
def inject_cloud_storage():
    # Utiliser image_url_service au lieu de cloud_storage
    import image_url_service
    return dict(cloud_storage=image_url_service)
```

Le module `image_url_service.py` contient une fonction `get_cloudinary_url()` compatible avec celle de l'ancien module `cloud_storage` :

```python
# Dans image_url_service.py
def get_cloudinary_url(image_path):
    """
    Fonction de compatibilité pour remplacer cloud_storage.get_cloudinary_url
    """
    return ImageUrlService.get_image_url(image_path)
```

### 5. Environnement de test

Un environnement de test a été créé pour vérifier le bon fonctionnement des corrections :

- Script `test_image_display.py` qui simule l'application principale
- Templates de test pour visualiser et éditer les exercices
- Fonctions pour créer des exercices de test avec différentes configurations d'images
- Interface pour exécuter les corrections et vérifier les résultats

## Comment tester les corrections

### Test local

1. Exécuter le script de test :
   ```
   python test_image_display.py
   ```

2. Accéder à l'interface de test à l'adresse : http://localhost:5001/

3. Cliquer sur "Créer des exercices de test" pour générer des exercices avec différentes configurations d'images

4. Tester l'édition d'exercices :
   - Vérifier que les images s'affichent correctement dans le formulaire d'édition
   - Tester l'upload d'une nouvelle image
   - Tester la suppression d'une image
   - Vérifier que les modifications sont correctement enregistrées

5. Exécuter la correction automatique :
   - Cliquer sur "Exécuter la correction" pour lancer la synchronisation des chemins d'images
   - Vérifier que les incohérences sont corrigées

### Test en production

1. Déployer les modifications sur l'environnement de production

2. Accéder à la route de synchronisation : `/fix-edit-image-display`

3. Vérifier le rapport généré pour s'assurer que les incohérences ont été corrigées

4. Tester l'édition de quelques exercices pour confirmer que les images s'affichent correctement

## Détails techniques

### Modifications dans `app.py`

```python
# Avant la modification
exercise.image_path = None  # L'image était stockée uniquement dans content['image']

# Après la modification
exercise.image_path = normalized_image_url  # L'image est stockée dans les deux emplacements
```

### Gestion de la suppression d'images

```python
# Logique ajoutée pour la suppression d'images
if 'remove_exercise_image' in request.form and request.form['remove_exercise_image'] == 'true':
    # Supprimer l'image à la fois de exercise.image_path et de content['image']
    if 'image' in content:
        del content['image']
    exercise.image_path = None
    exercise.content = json.dumps(content)
```

### Synchronisation des chemins d'images

```python
# Logique ajoutée pour synchroniser les chemins d'images
if exercise.image_path and not content.get('image'):
    content['image'] = normalize_image_path(exercise.image_path)
elif content.get('image') and not exercise.image_path:
    exercise.image_path = normalize_image_path(content['image'])
```

## Intégration dans l'application principale

Le blueprint `image_sync_bp` a été intégré dans l'application principale via la fonction `register_image_sync_routes` dans `app.py` :

```python
# Dans app.py
from fix_image_paths import register_image_sync_routes
register_image_sync_routes(app)
```

La fonction `register_image_sync_routes` a été modifiée pour éviter les enregistrements multiples du blueprint :

```python
# Dans fix_image_paths.py
def register_image_sync_routes(app):
    # Vérifier si le blueprint est déjà enregistré
    if 'image_sync' not in app.blueprints:
        app.register_blueprint(image_sync_bp, url_prefix='/image-sync')
        app.logger.info("Routes de synchronisation et correction d'images enregistrées")
    else:
        app.logger.info("Routes de synchronisation d'images déjà enregistrées")
```

Cette intégration permet d'accéder aux routes de synchronisation via les URLs suivantes :

- `/image-sync/check-image-consistency` : Vérification de la cohérence des chemins d'images
- `/image-sync/sync-image-paths` : Synchronisation des chemins d'images
- `/image-sync/fix-edit-image-display` : Correction spécifique pour l'affichage en édition
- `/image-sync/fix-single-exercise/<exercise_id>` : Correction d'un exercice spécifique

## Conclusion

Ces modifications garantissent que les images sont toujours stockées de manière cohérente entre `exercise.image_path` et le contenu JSON de l'exercice, ce qui résout le problème d'affichage des images lors de l'édition d'exercices.

La solution est compatible avec l'existant et ne nécessite pas de modifications des templates. Elle assure également une transition en douceur pour les exercices existants grâce aux routes de synchronisation intégrées à l'application principale.
