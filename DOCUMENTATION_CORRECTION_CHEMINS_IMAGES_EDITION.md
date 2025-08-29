# Correction des chemins d'images lors de la modification d'exercices

## Problèmes initiaux

1. **Problème principal**: Lors de la modification d'exercices existants, les images nouvellement ajoutées ou modifiées étaient placées dans un dossier générique `/static/uploads/` au lieu d'être organisées dans des sous-dossiers par type d'exercice comme lors de la création initiale d'exercices.

2. **Problème spécifique**: Certaines images avaient des chemins avec un double préfixe générique comme `/static/uploads/general/general_20250828_214...` qui n'étaient pas correctement normalisés lors de la modification d'exercices.

Ces problèmes créaient une incohérence dans l'organisation des fichiers et pouvaient potentiellement causer des problèmes d'affichage ou de gestion des images.

## Causes racines

1. **Cause principale**: La fonction `normalize_image_path` dans `utils/image_utils_no_normalize.py` ne prenait pas correctement en compte le paramètre `exercise_type` pour tous les cas de figure, notamment pour les chemins commençant par `uploads/` ou `/static/uploads/`.

2. **Cause spécifique**: La fonction ne gérait pas le cas particulier des chemins avec un double préfixe générique comme `/static/uploads/general/general_20250828_214...`, ce qui conduisait à des chemins incorrects lors de la modification d'exercices.

3. **Incohérence d'imports**: Il y avait une incohérence entre les imports dans `cloud_storage.py` (qui utilisait `image_utils.py`) et `app.py` (qui utilisait `image_utils_no_normalize.py`).

## Solution implémentée

### 1. Correction de la fonction `normalize_image_path`

La fonction a été améliorée pour garantir que tous les chemins d'images sont correctement normalisés avec le type d'exercice approprié, y compris le cas spécifique des chemins avec un double préfixe générique:

```python
def normalize_image_path(path, exercise_type=None):
    """
    Normalise le chemin d'image pour assurer un format cohérent avec le préfixe /static/
    et organise les images dans des sous-dossiers selon le type d'exercice
    
    Args:
        path (str): Le chemin d'image à normaliser
        exercise_type (str, optional): Le type d'exercice pour organiser les images dans des sous-dossiers
        
    Returns:
        str: Le chemin normalisé avec préfixe /static/ et sous-dossier du type d'exercice si nécessaire
    """
    if not path:
        return path
        
    # Normaliser le nom du fichier (remplacer les espaces par des underscores, supprimer les apostrophes)
    path = path.replace(' ', '_').replace("'", '')
    
    # Ignorer les URLs externes
    if path.startswith(('http://', 'https://')):
        return path
    
    # Cas spécifique: /static/uploads/general/general_TIMESTAMP_...
    if '/static/uploads/general/general_' in path:
        # Extraire le nom du fichier
        filename = path.split('/')[-1]
        
        # Si le nom commence par 'general_' et qu'on a un type d'exercice spécifique,
        # remplacer 'general_' par le type d'exercice
        if exercise_type and exercise_type != 'general' and filename.startswith('general_'):
            # Enlever le préfixe 'general_' pour éviter la duplication
            clean_filename = filename[8:]  # Longueur de 'general_'
            return f'/static/uploads/{exercise_type}/{exercise_type}_{clean_filename}'
        elif exercise_type and exercise_type != 'general':
            # Garder le nom tel quel mais changer le dossier
            return f'/static/uploads/{exercise_type}/{filename}'
        else:
            # Garder le chemin générique si pas de type spécifique
            return f'/static/uploads/{filename}'
    
    # Extraire le nom du fichier pour les autres cas
    filename = path.split('/')[-1]
    
    # Construire le chemin normalisé avec le type d'exercice si spécifié
    if exercise_type and exercise_type != 'general':
        return f'/static/uploads/{exercise_type}/{filename}'
    else:
        return f'/static/uploads/{filename}'
```

### 2. Correction de l'import dans `cloud_storage.py`

Pour assurer la cohérence, l'import dans `cloud_storage.py` a été modifié pour utiliser la même version de `normalize_image_path` que celle utilisée dans `app.py`:

```python
from utils.image_utils_no_normalize import normalize_image_path
```

### 3. Tests de validation

Un script de test `test_image_path_normalization.py` a été créé pour vérifier que la fonction `normalize_image_path` gère correctement tous les cas de figure avec le paramètre `exercise_type`, y compris le cas spécifique des chemins avec un double préfixe générique:

```python
def test_normalize_image_path_with_exercise_type():
    """Test la fonction normalize_image_path avec le paramètre exercise_type"""
    test_cases = [
        # Format: (input_path, exercise_type, expected_output)
        
        # Tests sans exercise_type (comportement par défaut)
        ("uploads/image.jpg", None, "/static/uploads/image.jpg"),
        ("image.jpg", None, "/static/uploads/image.jpg"),
        
        # Tests avec exercise_type spécifié
        ("uploads/image.jpg", "qcm", "/static/uploads/qcm/image.jpg"),
        ("image.jpg", "fill_in_blanks", "/static/uploads/fill_in_blanks/image.jpg"),
        
        # Tests avec chemins déjà préfixés
        ("/static/uploads/image.jpg", "qcm", "/static/uploads/qcm/image.jpg"),
        ("/static/uploads/general/image.jpg", "pairs", "/static/uploads/pairs/image.jpg"),
        
        # Cas spécifique: /static/uploads/general/general_TIMESTAMP_...
        ("/static/uploads/general/general_20250828_214402_abc123.jpg", "pairs", "/static/uploads/pairs/pairs_20250828_214402_abc123.jpg"),
        ("/static/uploads/general/general_20250828_214402_abc123.jpg", "qcm", "/static/uploads/qcm/qcm_20250828_214402_abc123.jpg"),
        ("/static/uploads/general/image_without_general_prefix.jpg", "qcm", "/static/uploads/qcm/image_without_general_prefix.jpg"),
    ]
    
    # Vérification que tous les cas passent
```

## Impact de la solution

1. **Organisation cohérente des fichiers**: Les images sont maintenant correctement organisées dans des sous-dossiers par type d'exercice, que ce soit lors de la création ou de la modification d'exercices.

2. **Prévention des chemins génériques**: Plus aucune image n'est placée dans le dossier générique `/static/uploads/general/` lors de la modification d'exercices.

3. **Correction des chemins avec double préfixe**: Les chemins problématiques comme `/static/uploads/general/general_20250828_214...` sont maintenant correctement normalisés en remplaçant le préfixe `general_` par le type d'exercice approprié.

4. **Simplification du code**: La logique de normalisation des chemins a été simplifiée et rendue plus robuste.

5. **Cohérence des imports**: Les mêmes fonctions sont maintenant utilisées dans tout le code pour la normalisation des chemins d'images.

## Fichiers modifiés

1. `utils/image_utils_no_normalize.py`: Correction de la fonction `normalize_image_path`
2. `cloud_storage.py`: Correction de l'import pour utiliser `image_utils_no_normalize`
3. `test_image_path_normalization.py`: Création d'un script de test pour valider la solution

## Tests effectués

- ✅ Vérification que tous les cas de normalisation de chemins fonctionnent correctement
- ✅ Vérification que les chemins d'images incluent bien le type d'exercice
- ✅ Vérification que les URLs externes ne sont pas modifiées
- ✅ Vérification que les chemins avec espaces et caractères spéciaux sont correctement normalisés
- ✅ Vérification que les chemins avec double préfixe générique sont correctement transformés
- ✅ Vérification que le préfixe `general_` est remplacé par le type d'exercice approprié

## Conclusion

Cette correction assure une gestion cohérente et robuste des chemins d'images lors de la création et de la modification d'exercices, facilitant ainsi l'organisation des fichiers et évitant les problèmes potentiels d'affichage ou de gestion des images.
