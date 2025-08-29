# Correction de l'affichage des images dans les exercices de type image_labeling

## Problème identifié

Les images ne s'affichent pas correctement après la création d'un exercice de type image_labeling. Ce problème est similaire à celui précédemment résolu pour les exercices de type légende.

### Causes techniques

1. **Chemins d'images incorrects** : 
   - Lors de la création d'un exercice image_labeling, le chemin de l'image est sauvegardé sans le préfixe `/static/` :
     ```python
     main_image_path = f'uploads/{unique_filename}'
     ```
   - Ce chemin est ensuite assigné à `content['main_image']` dans le JSON de l'exercice.

2. **Incohérence entre les champs** :
   - Le champ `exercise.image_path` et le champ `content['main_image']` ne sont pas synchronisés.
   - Les templates s'attendent à des chemins commençant par `/static/uploads/`.

3. **Problèmes de cache navigateur** :
   - Après modification d'un exercice, l'image peut rester en cache et ne pas se rafraîchir.

## Solution implémentée

### 1. Correction du code de création des exercices

Le script `fix_image_labeling_creation.py` modifie le code de création des exercices pour :

- Normaliser les chemins d'images avec le préfixe `/static/uploads/`
- Ajouter un paramètre de timestamp pour éviter les problèmes de cache

```python
# Avant
main_image_path = f'uploads/{unique_filename}'

# Après
main_image_path = f'/static/uploads/{unique_filename}'
```

### 2. Correction des exercices existants

Le script `fix_existing_image_labeling_exercises.py` corrige les exercices existants dans la base de données :

- Normalise les chemins d'images dans `exercise.image_path`
- Normalise les chemins d'images dans `content['main_image']`
- Synchronise les deux champs pour assurer la cohérence

### 3. Fonctions de normalisation des chemins

La fonction `normalize_image_path()` assure que tous les chemins d'images suivent le format standard :

```python
def normalize_image_path(path):
    """
    Normalise un chemin d'image pour s'assurer qu'il commence par /static/uploads/
    """
    if not path:
        return path
        
    # Supprimer le préfixe /static/ s'il existe déjà
    if path.startswith('/static/'):
        path = path[8:]  # Enlever '/static/'
        
    # Supprimer le préfixe static/ s'il existe
    if path.startswith('static/'):
        path = path[7:]  # Enlever 'static/'
        
    # S'assurer que le chemin commence par uploads/
    if not path.startswith('uploads/'):
        if '/' in path:
            # Si le chemin contient déjà un dossier, remplacer ce dossier par uploads
            path = 'uploads/' + path.split('/', 1)[1]
        else:
            # Sinon, ajouter le préfixe uploads/
            path = 'uploads/' + path
            
    # Ajouter le préfixe /static/
    return '/static/' + path
```

## Comment appliquer la correction

### Pour corriger le code de création

1. Exécuter le script `apply_image_labeling_fix.py` :
   ```
   python apply_image_labeling_fix.py
   ```

### Pour corriger les exercices existants

1. Exécuter le script `fix_existing_image_labeling_exercises.py` :
   ```
   python fix_existing_image_labeling_exercises.py
   ```
   - Suivre les instructions pour corriger un exercice spécifique ou tous les exercices.

## Vérification

Après application des corrections :

1. Créer un nouvel exercice de type image_labeling avec une image
2. Vérifier que l'image s'affiche correctement immédiatement après la création
3. Vérifier que l'image s'affiche correctement dans la page d'édition
4. Vérifier que les zones et étiquettes fonctionnent correctement

## Résultat attendu

- ✅ Les images s'affichent immédiatement après la création d'un exercice
- ✅ Les chemins d'images sont normalisés avec le préfixe `/static/uploads/`
- ✅ Les champs `exercise.image_path` et `content['main_image']` sont synchronisés
- ✅ Pas de problèmes de cache grâce au paramètre de timestamp
