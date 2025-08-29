# Documentation : Correction de l'affichage des images dans les exercices "Word Placement"

## Problème identifié

Lors de la création d'un nouvel exercice de type "word_placement" (mots à placer), les images téléchargées ne s'affichent pas correctement. Après analyse approfondie, nous avons identifié deux problèmes principaux :

1. **Absence de traitement spécifique pour l'image** : Dans la fonction `create_exercise` du fichier `modified_submit.py`, il n'existe pas de code spécifique pour traiter l'image téléchargée pour les exercices de type "word_placement", contrairement aux autres types d'exercices.

2. **Incohérence dans les noms de champs** : Le formulaire HTML utilise le nom `word_placement_image` pour le champ d'upload d'image, mais le code backend ne recherche pas spécifiquement ce champ.

## Analyse technique

### 1. Formulaire HTML (create_exercise_simple.html)

Le formulaire HTML est correctement configuré avec un champ d'upload d'image nommé `word_placement_image` :

```html
<input type="file" name="word_placement_image" class="form-control" accept="image/*" 
       onchange="setupImagePreview('word_placement_image', 'word_placement_image_preview', 'word_placement_preview_img')">
```

### 2. Fonction create_exercise (modified_submit.py)

Dans la fonction `create_exercise`, le code pour le type "word_placement" ne traite pas l'image téléchargée :

```python
elif exercise_type == 'word_placement':
    # Récupération des phrases et des mots
    sentences = request.form.getlist('sentences[]')
    words = request.form.getlist('words[]')
    
    # Validation et nettoyage des données
    
    # Construction du contenu JSON
    content = {
        'sentences': sentences,
        'words': words
    }
    
    # PROBLÈME : Aucun traitement de l'image ici
    # Pas de récupération de request.files['word_placement_image']
    # Pas de sauvegarde de l'image
    # Pas de mise à jour de exercise_image_path
    # Pas d'ajout de l'image dans le contenu JSON
```

### 3. Template d'affichage (word_placement.html)

Le template `word_placement.html` est correctement configuré pour afficher l'image si `exercise.image_path` est défini :

```html
{% if exercise.image_path %}
<div class="exercise-image-container mb-4">
    <img src="{{ cloud_storage.get_cloudinary_url(exercise.image_path) }}" 
         alt="Image d'illustration" class="img-fluid rounded">
</div>
{% endif %}
```

## Solution implémentée

La solution consiste à ajouter le traitement de l'image dans la section "word_placement" de la fonction `create_exercise` :

```python
# CORRECTION: Traitement de l'image spécifique pour word_placement
if 'word_placement_image' in request.files:
    image_file = request.files['word_placement_image']
    if image_file and image_file.filename != '' and allowed_file(image_file.filename):
        # Sécuriser le nom du fichier
        filename = secure_filename(image_file.filename)
        
        # Ajouter un timestamp pour éviter les conflits de noms
        unique_filename = f"{int(time.time())}_{filename}"
        
        # Créer le répertoire s'il n'existe pas
        upload_folder = os.path.join('static', 'uploads', 'word_placement')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Sauvegarder l'image
        image_path = os.path.join(upload_folder, unique_filename)
        image_file.save(image_path)
        
        # Normaliser le chemin pour la base de données
        normalized_path = f'/static/uploads/word_placement/{unique_filename}'
        
        # Stocker le chemin normalisé pour la base de données
        exercise_image_path = normalized_path
        
        # Ajouter le chemin de l'image au contenu JSON
        content['image'] = normalized_path
```

Cette correction :

1. Vérifie si une image a été téléchargée avec le nom `word_placement_image`
2. Sécurise le nom du fichier et ajoute un timestamp pour éviter les conflits
3. Crée le répertoire de destination s'il n'existe pas
4. Sauvegarde l'image physiquement sur le serveur
5. Normalise le chemin pour la base de données (avec le préfixe `/static/`)
6. Met à jour la variable `exercise_image_path` qui sera utilisée pour créer l'exercice
7. Ajoute également le chemin de l'image dans le contenu JSON de l'exercice

## Script de correction

Un script `fix_word_placement_image_upload.py` a été créé pour :

1. Vérifier que le formulaire HTML est correctement configuré
2. Modifier le fichier `modified_submit.py` pour ajouter le traitement de l'image
3. Tester la correction sur un exercice existant

## Résultats attendus

Après cette correction :

1. Les images téléchargées lors de la création d'un nouvel exercice "word_placement" seront correctement sauvegardées
2. Le chemin de l'image sera correctement stocké dans `exercise.image_path`
3. L'image sera également stockée dans le contenu JSON de l'exercice
4. Le template affichera correctement l'image grâce à `cloud_storage.get_cloudinary_url(exercise.image_path)`

## Recommandations supplémentaires

1. **Uniformisation des noms de champs** : Envisager d'uniformiser les noms des champs d'upload d'image pour tous les types d'exercices (par exemple, utiliser toujours `exercise_image`).

2. **Fonction helper pour le traitement des images** : Créer une fonction helper pour traiter les images de manière cohérente pour tous les types d'exercices.

3. **Validation côté client** : Ajouter une validation côté client pour les formats d'image acceptés et la taille maximale.

4. **Logs de débogage** : Ajouter des logs de débogage pour faciliter le diagnostic des problèmes d'upload d'images.

## Conclusion

Cette correction résout le problème d'affichage des images dans les exercices "word_placement" en assurant que les images téléchargées sont correctement traitées, sauvegardées et associées à l'exercice. La solution est cohérente avec le traitement des images pour les autres types d'exercices et respecte les conventions de nommage et de stockage des fichiers de l'application.
