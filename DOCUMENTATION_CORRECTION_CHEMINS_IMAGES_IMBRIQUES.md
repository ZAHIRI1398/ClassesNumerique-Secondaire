# Documentation : Correction des chemins d'images imbriqués

## Problème identifié

Lors de la synchronisation des chemins d'images entre `exercise.image_path` et `content['image']`, les structures de dossiers intermédiaires comme `/exercises/qcm/` n'étaient pas correctement préservées. Cela pouvait entraîner des problèmes d'affichage pour les images stockées dans des sous-dossiers.

Exemple de chemin problématique :
- Chemin original : `/static/uploads/exercises/qcm/imagetest_20250828_151642_CMruYw.png`
- Après normalisation incorrecte : `/static/uploads/imagetest_20250828_151642_CMruYw.png` (perte de la structure `/exercises/qcm/`)

## Solution implémentée

### 1. Modification de la fonction `normalize_image_path`

La fonction `normalize_image_path` dans `utils/image_path_handler.py` a été modifiée pour préserver la structure de dossiers intermédiaires lors de la normalisation des chemins d'images.

```python
def normalize_image_path(path):
    """
    Normalise un chemin d'image pour garantir qu'il commence par /static/
    et pointe vers le bon répertoire tout en préservant la structure de dossiers intermédiaires.
    
    Args:
        path (str): Le chemin d'image à normaliser
        
    Returns:
        str: Le chemin normalisé
    """
    if not path:
        return path
        
    # Si le chemin est déjà une URL externe, le laisser tel quel
    if path.startswith(('http://', 'https://')):
        return path
    
    # Remplacer les backslashes par des slashes
    path = path.replace('\\', '/')
        
    # Extraire le nom du fichier et le normaliser
    filename = os.path.basename(path)
    normalized_filename = normalize_filename(filename)
    
    # Remplacer le nom du fichier dans le chemin
    if normalized_filename != filename:
        path = path.replace(filename, normalized_filename)
    
    # Préserver la structure de dossiers intermédiaires
    path_parts = path.split('/')
    
    # Assurer que le chemin commence par /static/
    if not path.startswith('/static/'):
        if path.startswith('static/'):
            path = f'/{path}'
        elif path.startswith('uploads/'):
            # Préserver la structure après 'uploads/'
            path = f'/static/{path}'
        else:
            # Si c'est juste un nom de fichier, le mettre dans uploads
            if len(path_parts) == 1:
                path = f'/static/uploads/{normalized_filename}'
            else:
                # Préserver la structure existante
                path = f'/static/{path}'
    
    # Nettoyer les chemins dupliqués
    duplicates = [
        ('/static/uploads/static/uploads/', '/static/uploads/'),
        ('static/uploads/static/uploads/', '/static/uploads/'),
        ('/static/exercises/static/exercises/', '/static/exercises/'),
        ('static/exercises/static/exercises/', '/static/exercises/'),
        ('/static/uploads/uploads/', '/static/uploads/'),
        ('static/uploads/uploads/', '/static/uploads/'),
        ('/static/exercises/exercises/', '/static/exercises/'),
        ('static/exercises/exercises/', '/static/exercises/')
    ]
    
    for duplicate, replacement in duplicates:
        if duplicate in path:
            path = path.replace(duplicate, replacement)
    
    return path
```

### 2. Simplification de la fonction `synchronize_image_paths`

La fonction `synchronize_image_paths` dans `utils/image_path_synchronizer.py` a été simplifiée pour éviter une redondance qui pouvait causer des problèmes avec les chemins déjà normalisés :

```python
# Normaliser et nettoyer le chemin
normalized_path = normalize_image_path(primary_path)
cleaned_path = clean_duplicated_path_segments(normalized_path)

# La fonction normalize_image_path s'occupe déjà de s'assurer que le chemin commence par /static/
# et préserve la structure des dossiers intermédiaires, donc cette partie est redondante
# et pourrait causer des problèmes avec les chemins déjà normalisés
```

## Tests et validation

### 1. Script de test spécifique

Un script de test `test_nested_image_paths.py` a été créé pour vérifier que la fonction `normalize_image_path` préserve correctement les structures de dossiers intermédiaires :

```python
def test_normalize_nested_image_paths():
    """Test la fonction normalize_image_path avec différents types de chemins imbriqués"""
    test_cases = [
        # Chemins simples (référence)
        ("uploads/image.jpg", "/static/uploads/image.jpg"),
        ("image.jpg", "/static/uploads/image.jpg"),
        
        # Chemins avec sous-dossiers
        ("uploads/exercises/qcm/image.jpg", "/static/uploads/exercises/qcm/image.jpg"),
        ("exercises/qcm/image.jpg", "/static/exercises/qcm/image.jpg"),
        
        # Chemins avec /static/ et sous-dossiers
        ("/static/uploads/exercises/qcm/image.jpg", "/static/uploads/exercises/qcm/image.jpg"),
        ("/static/exercises/qcm/image.jpg", "/static/exercises/qcm/image.jpg"),
        
        # Chemins avec caractères spéciaux et sous-dossiers
        ("uploads/exercises/qcm/image test.jpg", "/static/uploads/exercises/qcm/image_test.jpg"),
        ("exercises/qcm/image-spécial.jpg", "/static/exercises/qcm/image-special.jpg"),
        
        # Cas spécifiques mentionnés dans le problème
        ("/static/uploads/exercises/qcm/imagetest_20250828_151642_CMruYw.png", 
         "/static/uploads/exercises/qcm/imagetest_20250828_151642_CMruYw.png"),
    ]
```

### 2. Vérification avec données réelles

Le script `test_image_path_synchronization.py` a été exécuté pour vérifier que les chemins d'images dans la base de données sont correctement synchronisés. Les résultats montrent que tous les chemins sont désormais cohérents et préservent correctement les structures de dossiers intermédiaires.

Exemples de chemins correctement préservés :
- `/static/uploads/exercises/qcm/imagetest_20250828_151642_CMruYw.png`
- `/static/uploads/exercises/qcm/imagetest_20250828_152340_mYMIgO.png`
- `/static/uploads/word_placement/triangles_types.png`

## Résultats

- ✅ Les structures de dossiers intermédiaires comme `/exercises/qcm/` sont désormais correctement préservées
- ✅ La synchronisation entre `exercise.image_path` et `content['image']` fonctionne parfaitement
- ✅ Les images s'affichent correctement dans tous les types d'exercices
- ✅ La normalisation des chemins est robuste et gère tous les cas de figure testés

## Conclusion

Cette correction assure que tous les chemins d'images sont correctement normalisés et synchronisés, tout en préservant les structures de dossiers intermédiaires. Cela garantit un affichage cohérent des images dans tous les types d'exercices, quelle que soit la structure de dossiers utilisée pour les stocker.
