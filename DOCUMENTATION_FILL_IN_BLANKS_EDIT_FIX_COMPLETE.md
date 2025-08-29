# Correction de l'édition des exercices "Fill in Blanks" (Texte à trous)

## Problème identifié

L'édition des exercices de type "fill_in_blanks" (texte à trous) ne fonctionne pas correctement. Lorsqu'un enseignant modifie un exercice existant via le formulaire d'édition, les changements apportés aux phrases et aux mots ne sont pas sauvegardés. De plus, la gestion des images associées à ces exercices (ajout, modification, suppression) n'est pas correctement implémentée.

### Causes du problème

1. **Traitement POST incomplet** : La route `/exercise/<int:exercise_id>/edit` dans `app.py` ne traite pas spécifiquement les données POST pour les exercices de type "fill_in_blanks". Elle utilise un traitement générique qui ne récupère pas les champs `sentences[]` et `words[]` du formulaire.

2. **Absence de mise à jour du contenu JSON** : Le contenu JSON spécifique aux exercices "fill_in_blanks" n'est pas mis à jour avec les nouvelles phrases et mots.

3. **Gestion incomplète des images** : Le code actuel ne gère pas correctement l'ajout, le remplacement ou la suppression des images associées aux exercices.

## Solution proposée

La solution consiste à ajouter un traitement spécifique pour les exercices de type "fill_in_blanks" dans la route d'édition, qui :

1. Récupère correctement les listes `sentences[]` et `words[]` du formulaire
2. Valide ces données (présence de phrases et mots, trous dans les phrases, nombre suffisant de mots)
3. Gère l'ajout, le remplacement et la suppression des images
4. Met à jour le contenu JSON de l'exercice
5. Sauvegarde les modifications en base de données

### Détails de la solution

#### 1. Récupération des données du formulaire

```python
sentences = request.form.getlist('sentences[]')
words = request.form.getlist('words[]')
```

#### 2. Validation des données

```python
# Vérifier la présence de phrases
if not sentences:
    flash('Veuillez ajouter au moins une phrase.', 'error')
    return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)

# Vérifier la présence de mots
if not words:
    flash('Veuillez ajouter au moins un mot.', 'error')
    return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)

# Vérifier que chaque phrase contient au moins un trou
for i, sentence in enumerate(sentences):
    if '___' not in sentence:
        flash(f'La phrase {i+1} ne contient pas de trous (utilisez ___ pour marquer les trous).', 'error')
        return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)

# Vérifier qu'il y a assez de mots pour tous les trous
total_blanks = sum(sentence.count('___') for sentence in sentences)
if len(words) < total_blanks:
    flash(f'Il n\'y a pas assez de mots ({len(words)}) pour remplir tous les trous ({total_blanks}).', 'error')
    return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
```

#### 3. Gestion des images

```python
# 1. Vérifier si l'utilisateur veut supprimer l'image existante
if request.form.get('remove_exercise_image') == 'true' and exercise.image_path:
    try:
        # Supprimer l'ancienne image du système de fichiers
        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(exercise.image_path))
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
        
        # Mettre à jour le chemin de l'image dans l'exercice
        exercise.image_path = None
    except Exception as e:
        flash('Erreur lors de la suppression de l\'image', 'error')

# 2. Vérifier si l'utilisateur a téléversé une nouvelle image
if 'exercise_image' in request.files:
    file = request.files['exercise_image']
    if file and file.filename != '' and allowed_file(file.filename):
        try:
            # Supprimer l'ancienne image si elle existe
            if exercise.image_path:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(exercise.image_path))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Sauvegarder la nouvelle image
            filename = generate_unique_filename(file.filename)
            dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'exercises')
            os.makedirs(dest_folder, exist_ok=True)
            file_path = os.path.join(dest_folder, filename)
            file.save(file_path)
            exercise.image_path = f'/static/uploads/exercises/{filename}'
        except Exception as e:
            flash('Erreur lors de l\'upload de l\'image', 'error')
```

#### 4. Mise à jour du contenu JSON

```python
content = json.loads(exercise.content) if exercise.content else {}
content['sentences'] = sentences
content['words'] = words
exercise.content = json.dumps(content)
```

#### 5. Sauvegarde en base de données

```python
try:
    db.session.commit()
    flash(f'Exercice "{exercise.title}" modifié avec succès!', 'success')
    return redirect(url_for('view_exercise', exercise_id=exercise.id))
except Exception as e:
    db.session.rollback()
    flash(f'Erreur lors de la modification de l\'exercice: {str(e)}', 'error')
    return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
```

## Instructions d'intégration

Pour intégrer cette correction dans le code existant :

1. Ouvrez le fichier `app.py`
2. Recherchez la route `edit_exercise` et le bloc qui traite la méthode POST
3. Localisez la section qui commence par :
   ```python
   else:
       # Gestion générique pour tous les autres types d'exercices
       # (fill_in_blanks, word_placement, drag_and_drop, etc.)
       current_app.logger.info(f'[EDIT_DEBUG] Traitement générique pour le type: {exercise.exercise_type}')
   ```
4. Juste avant cette section, ajoutez le bloc de code spécifique pour les exercices "fill_in_blanks" comme indiqué dans le fichier `fix_fill_in_blanks_edit_complete.py`

## Tests

Un script de test complet `test_fill_in_blanks_edit_image.py` a été créé pour valider la correction. Ce script teste :

1. L'ajout d'une nouvelle image à un exercice sans image
2. Le remplacement d'une image existante
3. La suppression d'une image existante
4. La validation des données (phrases, mots, trous)
5. La gestion des erreurs de base de données

Pour exécuter les tests :

```bash
python test_fill_in_blanks_edit_image.py
```

## Avantages de cette correction

1. **Fonctionnalité complète** : Les enseignants peuvent maintenant modifier les phrases, les mots et les images des exercices "fill_in_blanks".
2. **Validation robuste** : Les données sont validées avant sauvegarde pour éviter les exercices invalides.
3. **Gestion optimisée des images** : Ajout, remplacement et suppression d'images avec nettoyage des anciennes images.
4. **Feedback utilisateur** : Messages d'erreur et de succès clairs pour guider l'utilisateur.
5. **Sécurité améliorée** : Validation des types de fichiers et gestion des erreurs.

## Conclusion

Cette correction résout complètement le problème d'édition des exercices "fill_in_blanks" en permettant la modification des phrases, des mots et des images associées. La solution est robuste, sécurisée et offre une bonne expérience utilisateur.
