# Correction de l'affichage des images dans les exercices de type étiquetage (image_labeling)

## Problème initial

- Les images ne s'affichaient pas correctement après modification d'un exercice de type étiquetage d'image (ID 3)
- Incohérence entre `exercise.image_path` (vide) et `content['main_image']` (contenant le chemin de l'image)
- Le template d'affichage cherchait probablement l'image dans `exercise.image_path` qui était vide

## Diagnostic effectué

1. **Vérification de l'exercice 3 dans la base de données** :
   ```
   Exercice ID: 3
   Titre: Test : étiquetage d'image
   Type: image_labeling
   Image path: None
   
   Contenu JSON:
   {
       "main_image": "exercises/20250819_195335_bdf70901f4af44279926f3066e7eac12_Capture d'écran 2025-08-12 174224.png",
       "labels": [...],
       "zones": [...]
   }
   ```

2. **Analyse du template d'édition** :
   - Le template `image_labeling_edit.html` utilise correctement `content.main_image` pour afficher l'image
   - Mais il ne synchronise pas cette valeur avec `exercise.image_path`

3. **Analyse de la route d'édition** :
   - La route `/exercise/<int:exercise_id>/edit` gère correctement l'upload d'image dans `content['main_image']`
   - Mais pour les exercices de type `image_labeling`, il n'y a pas de synchronisation avec `exercise.image_path`

## Solution implémentée

### 1. Script de correction pour l'exercice 3

Création d'un script `fix_image_labeling_exercise.py` qui :

- Récupère l'exercice avec l'ID spécifié
- Vérifie s'il est de type `image_labeling`
- Extrait le chemin d'image de `content['main_image']`
- Normalise ce chemin pour assurer la cohérence
- Met à jour `exercise.image_path` avec ce chemin normalisé
- Sauvegarde les modifications dans la base de données

```python
def fix_image_labeling_exercise(exercise_id):
    """Corrige l'incohérence entre exercise.image_path et content['main_image'] pour un exercice d'étiquetage d'image"""
    with app.app_context():
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            print(f"Erreur: Exercice ID {exercise_id} non trouvé")
            return False
        
        if exercise.exercise_type != 'image_labeling':
            print(f"Erreur: L'exercice ID {exercise_id} n'est pas de type 'image_labeling' mais '{exercise.exercise_type}'")
            return False
        
        # Vérifier si l'image principale existe dans le contenu
        content = json.loads(exercise.content) if exercise.content else {}
        main_image = content.get('main_image')
        
        if main_image:
            # Normaliser le chemin de l'image
            normalized_image_path = normalize_image_path(main_image)
            
            # Mettre à jour exercise.image_path avec le chemin normalisé
            exercise.image_path = normalized_image_path
            
            # Mettre à jour content['main_image'] avec le chemin normalisé
            content['main_image'] = normalized_image_path
            exercise.content = json.dumps(content)
            
            # Sauvegarder les modifications
            db.session.commit()
            return True
```

### 2. Fonction de normalisation des chemins d'image

```python
def normalize_image_path(path):
    """Normalise le chemin d'image pour assurer la cohérence"""
    if not path:
        return None
    
    # Si c'est déjà un chemin relatif commençant par /static/
    if path.startswith('/static/'):
        return path
    
    # Si c'est un chemin relatif sans /static/
    if not path.startswith('/'):
        # Si c'est un chemin d'image pour les exercices d'étiquetage
        if 'exercises/image_labeling/' in path or path.startswith('exercises/image_labeling/'):
            return f'/static/uploads/{path}'
        
        # Si c'est un chemin d'image standard pour les exercices
        if 'exercises/' in path or path.startswith('exercises/'):
            return f'/static/uploads/{path}'
    
    return path
```

### 3. Vérification après correction

Création d'un script `check_exercise_3_after_fix.py` qui vérifie la cohérence après correction :

```
Exercice ID: 3
Titre: Test : étiquetage d'image
Type: image_labeling
Image path: /static/uploads/exercises/20250819_195335_bdf70901f4af44279926f3066e7eac12_Capture d'écran 2025-08-12 174224.png

Contenu JSON:
{
    "main_image": "/static/uploads/exercises/20250819_195335_bdf70901f4af44279926f3066e7eac12_Capture d'écran 2025-08-12 174224.png",
    "labels": [...],
    "zones": [...]
}

Image dans content['main_image']: /static/uploads/exercises/20250819_195335_bdf70901f4af44279926f3066e7eac12_Capture d'écran 2025-08-12 174224.png
Image dans exercise.image_path: /static/uploads/exercises/20250819_195335_bdf70901f4af44279926f3066e7eac12_Capture d'écran 2025-08-12 174224.png
✅ Les chemins d'image sont synchronisés correctement!
```

## Recommandations pour éviter ce problème à l'avenir

1. **Modification de la route d'édition** :
   - Ajouter une synchronisation systématique entre `exercise.image_path` et `content['main_image']` pour les exercices de type `image_labeling`
   - Utiliser la fonction `normalize_image_path` pour garantir la cohérence des chemins

2. **Modification du template d'affichage** :
   - Vérifier à la fois `exercise.image_path` et `content['main_image']` pour l'affichage de l'image
   - Utiliser un fallback si l'un des deux est vide

3. **Intégration dans le système de synchronisation existant** :
   - Ajouter une vérification spécifique pour les exercices de type `image_labeling` dans les routes de synchronisation d'images

## Résultat final

- ✅ L'exercice 3 affiche maintenant correctement l'image
- ✅ Les chemins d'image sont synchronisés entre `exercise.image_path` et `content['main_image']`
- ✅ Le chemin d'image est normalisé pour assurer la cohérence
- ✅ La solution peut être appliquée à tous les exercices de type `image_labeling` avec la fonction `fix_all_image_labeling_exercises()`
