# Documentation : Correction de l'affichage des images dans les exercices Word Placement

## Problème identifié

Certains exercices de type "word_placement" ne s'affichaient pas correctement car ils n'avaient pas d'image associée ou le chemin d'image était incorrect. Le problème a été identifié dans l'exercice "Test mots à placerComplet" qui n'avait pas d'image définie dans sa propriété `image_path` ni dans son contenu JSON.

## Diagnostic réalisé

Un script de diagnostic a été créé pour analyser les exercices de type "word_placement" et vérifier :
- Si l'exercice a une propriété `image_path` définie
- Si l'image référencée existe physiquement sur le serveur
- Si le contenu JSON de l'exercice contient également une référence à l'image
- Si les autres propriétés nécessaires (words, sentences) sont correctement définies

Le diagnostic a révélé que l'exercice "Test mots à placerComplet" n'avait pas d'image associée, alors que le template `word_placement.html` s'attend à afficher une image si `exercise.image_path` est défini.

## Solution implémentée

1. **Création d'une image adaptée** : Une image représentant différents types de triangles a été créée et stockée dans le répertoire `static/uploads/word_placement/`.

2. **Association de l'image à l'exercice** : L'image a été associée à l'exercice en :
   - Mettant à jour la propriété `image_path` de l'exercice avec le chemin `/static/uploads/word_placement/triangles_types.png`
   - Ajoutant la référence à l'image dans le contenu JSON de l'exercice

3. **Vérification de l'affichage** : Après ces modifications, l'image s'affiche correctement dans l'exercice "Test mots à placerComplet".

## Mécanisme d'affichage des images

Le template `word_placement.html` utilise le code suivant pour afficher l'image de l'exercice :

```html
{% if exercise.image_path %}
    <img src="{{ cloud_storage.get_cloudinary_url(exercise.image_path) }}" 
         alt="Image de l'exercice" 
         class="img-fluid rounded shadow" 
         style="max-height: 400px;">
{% endif %}
```

Ce code vérifie si `exercise.image_path` est défini et, si c'est le cas, utilise la fonction `cloud_storage.get_cloudinary_url()` pour obtenir l'URL de l'image.

## Service cloud_storage

Le service `cloud_storage` est injecté dans le contexte des templates via le code suivant dans `app.py` :

```python
@app.context_processor
def inject_cloud_storage():
    # Utiliser image_url_service au lieu de cloud_storage
    import image_url_service
    return dict(cloud_storage=image_url_service)
```

Le service `image_url_service` fournit une fonction `get_cloudinary_url()` qui :
1. Normalise le chemin d'image
2. Nettoie les chemins dupliqués (comme `/static/uploads/static/uploads/`)
3. Vérifie si l'image existe physiquement sur le serveur
4. Retourne une URL valide pour l'image

## Recommandations pour éviter ce problème à l'avenir

1. **Validation lors de la création d'exercices** : Ajouter une validation pour s'assurer que les exercices de type "word_placement" ont une image associée.

2. **Interface d'édition améliorée** : Améliorer l'interface d'édition des exercices pour faciliter l'ajout d'images.

3. **Diagnostic régulier** : Exécuter régulièrement le script de diagnostic pour identifier les exercices sans image ou avec des images manquantes.

4. **Documentation des types d'exercices** : Documenter clairement les propriétés requises pour chaque type d'exercice, y compris si une image est nécessaire.

## Scripts créés

### Script de diagnostic

Un script `diagnose_word_placement_images.py` a été créé pour diagnostiquer les problèmes d'affichage d'images dans les exercices de type "word_placement". Ce script :
- Vérifie si l'exercice a une propriété `image_path` définie
- Vérifie si l'image référencée existe physiquement sur le serveur
- Vérifie si le contenu JSON de l'exercice contient également une référence à l'image
- Vérifie si les autres propriétés nécessaires (words, sentences) sont correctement définies

### Script d'ajout d'image

Un script `add_image_to_word_placement.py` a été créé pour ajouter une image à l'exercice "Test mots à placerComplet". Ce script :
- Crée une image représentant différents types de triangles
- Trouve l'exercice "Test mots à placerComplet" dans la base de données
- Met à jour la propriété `image_path` de l'exercice
- Ajoute la référence à l'image dans le contenu JSON de l'exercice

Ces scripts peuvent être réutilisés pour diagnostiquer et corriger d'autres exercices de type "word_placement" qui auraient des problèmes similaires.
