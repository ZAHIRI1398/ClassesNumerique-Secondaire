# Documentation : Correction de l'affichage des images dans l'interface d'édition des exercices de paires

## Problème initial

L'interface d'édition des exercices d'association de paires (`pairs_edit.html`) présentait un problème d'affichage des images. Lors de la modification d'un exercice existant, les images n'étaient pas correctement affichées et une erreur était générée :

```
TypeError: get_cloudinary_url() takes 1 positional argument but 2 were given
```

Cette erreur se produisait car le template appelait `cloud_storage.get_cloudinary_url(image_path, 'pairs')` avec deux arguments, alors que la fonction exposée aux templates n'acceptait qu'un seul argument.

## Analyse du problème

Après investigation, nous avons identifié les causes suivantes :

1. **Conflit de noms** : Dans `app.py`, la fonction `inject_cloud_storage()` exposait le module `image_url_service` sous le nom `cloud_storage` dans les templates, écrasant ainsi le module `cloud_storage` réel.

2. **Signatures de fonctions incompatibles** :
   - La fonction `get_cloudinary_url` dans `cloud_storage.py` accepte deux arguments : `image_path` et `exercise_type=None`
   - La fonction `get_cloudinary_url` dans `image_url_service.py` n'accepte qu'un seul argument : `image_path`

3. **Exposition incorrecte aux templates** : Bien que le module `cloud_storage` était exposé via `app.jinja_env.globals`, il était écrasé par la fonction `inject_cloud_storage()` qui exposait `image_url_service` sous le même nom.

## Solution implémentée

### 1. Modification de la fonction d'injection de contexte

Nous avons renommé la fonction `inject_cloud_storage()` en `inject_image_url_service()` et modifié son comportement pour exposer `image_url_service` sous son propre nom, évitant ainsi le conflit avec `cloud_storage` :

```python
# Avant
@app.context_processor
def inject_cloud_storage():
    return dict(cloud_storage=image_url_service)

# Après
@app.context_processor
def inject_image_url_service():
    return dict(image_url_service=image_url_service)
```

### 2. Exposition directe de la fonction get_cloudinary_url

Nous avons maintenu l'exposition de la fonction `get_cloudinary_url` de `cloud_storage` directement dans les templates via :

```python
app.jinja_env.globals.update(get_cloudinary_url=cloud_storage.get_cloudinary_url)
```

### 3. Modification du template pairs_edit.html

Nous avons modifié le template `pairs_edit.html` pour utiliser directement la fonction `get_cloudinary_url` sans le préfixe `cloud_storage` :

```html
<!-- Avant -->
<img src="{{ cloud_storage.get_cloudinary_url(pair.left.content, 'pairs') }}?v={{ range(100000, 999999) | random }}" 
     alt="Image gauche" class="img-thumbnail" style="max-height: 100px;" 
     onerror="this.onerror=null; this.src='/static/images/placeholder-image.png'; this.style.opacity='0.7';">

<!-- Après -->
<img src="{{ get_cloudinary_url(pair.left.content) }}?v={{ range(100000, 999999) | random }}" 
     alt="Image gauche" class="img-thumbnail" style="max-height: 100px;" 
     onerror="this.onerror=null; this.src='/static/images/placeholder-image.png'; this.style.opacity='0.7';">
```

## Tests et validation

La solution a été testée avec succès à l'aide du script `test_pairs_edit_template.py` qui vérifie :
1. L'appel direct à `cloud_storage.get_cloudinary_url` avec un et deux arguments
2. Le rendu d'un template simulant l'utilisation dans `pairs_edit.html`

Les tests confirment que la fonction `get_cloudinary_url` accepte désormais correctement les deux formes d'appel :
- `get_cloudinary_url(image_path)` → `/static/exercises/general/image_path`
- `get_cloudinary_url(image_path, 'pairs')` → `/static/exercises/pairs/image_path`

## Recommandations pour l'avenir

1. **Cohérence des noms** : Maintenir une distinction claire entre `cloud_storage` et `image_url_service` dans tout le code.
2. **Documentation des fonctions** : Documenter clairement les signatures des fonctions exposées aux templates.
3. **Tests automatisés** : Conserver et étendre les tests pour détecter rapidement les problèmes similaires.
4. **Revue de code** : Vérifier les autres templates qui pourraient utiliser `cloud_storage.get_cloudinary_url` et les adapter si nécessaire.

## Conclusion

Cette correction résout le problème d'affichage des images dans l'interface d'édition des exercices de paires en éliminant le conflit entre les modules `cloud_storage` et `image_url_service`, et en assurant que la fonction `get_cloudinary_url` est correctement exposée aux templates avec sa signature complète.
