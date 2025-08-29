# Correction du problème d'édition des exercices "fill_in_blanks"

## Problème identifié

Lors de l'édition d'un exercice de type "fill_in_blanks" (texte à trous), les modifications apportées aux phrases et aux mots ne sont pas sauvegardées correctement. Après analyse du code, nous avons identifié que:

1. Le formulaire HTML (`fill_in_blanks_edit.html`) envoie correctement les données avec les noms de champs `sentences[]` et `words[]`.
2. La route d'édition principale (`edit_exercise` dans `app.py`) ne traite pas spécifiquement les données POST pour le type "fill_in_blanks".
3. Le traitement générique pour les types d'exercices non spécifiés ne met à jour que les champs de base (titre, description, image) mais ne reconstruit pas le contenu JSON spécifique au type d'exercice.
4. Par conséquent, les modifications des phrases et des mots sont perdues lors de la sauvegarde.

## Solution proposée

Nous avons créé deux fichiers:

1. `fix_fill_in_blanks_edit.py`: Contient la fonction de correction et les instructions d'intégration.
2. `test_fill_in_blanks_edit.py`: Script de test pour valider la correction.

### Modifications à apporter

Dans la route `edit_exercise` de `app.py`, il faut ajouter un bloc spécifique pour traiter les exercices de type "fill_in_blanks", juste avant le bloc de traitement générique:

```python
elif exercise.exercise_type == 'fill_in_blanks':
    current_app.logger.info(f'[EDIT_DEBUG] Traitement spécifique pour fill_in_blanks')
    
    # Récupérer les phrases et les mots du formulaire
    sentences = request.form.getlist('sentences[]')
    words = request.form.getlist('words[]')
    
    # Validation des données
    if not sentences:
        flash('Veuillez ajouter au moins une phrase.', 'error')
        content = json.loads(exercise.content) if exercise.content else {}
        return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    
    if not words:
        flash('Veuillez ajouter au moins un mot.', 'error')
        content = json.loads(exercise.content) if exercise.content else {}
        return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    
    # Vérifier que chaque phrase contient au moins un trou
    for i, sentence in enumerate(sentences):
        if '___' not in sentence:
            flash(f'La phrase {i+1} ne contient pas de trous (utilisez ___ pour marquer les trous).', 'error')
            content = json.loads(exercise.content) if exercise.content else {}
            return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    
    # Vérifier qu'il y a assez de mots pour tous les trous
    total_blanks = sum(sentence.count('___') for sentence in sentences)
    if len(words) < total_blanks:
        flash(f'Il n\'y a pas assez de mots ({len(words)}) pour remplir tous les trous ({total_blanks}).', 'error')
        content = json.loads(exercise.content) if exercise.content else {}
        return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    
    # Mettre à jour le contenu JSON
    content = json.loads(exercise.content) if exercise.content else {}
    content['sentences'] = sentences
    content['words'] = words
    
    # Sauvegarder le contenu JSON dans l'exercice
    exercise.content = json.dumps(content)
    current_app.logger.info(f'[EDIT_DEBUG] Contenu fill_in_blanks mis à jour: {exercise.content}')
    
    try:
        db.session.commit()
        flash(f'Exercice "{exercise.title}" modifié avec succès!', 'success')
        return redirect(url_for('view_exercise', exercise_id=exercise.id))
    except Exception as e:
        current_app.logger.error(f'[EDIT_DEBUG] Erreur lors de la sauvegarde: {str(e)}')
        db.session.rollback()
        flash(f'Erreur lors de la modification de l\'exercice: {str(e)}', 'error')
        content = json.loads(exercise.content) if exercise.content else {}
        return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
```

### Validation

Le script de test `test_fill_in_blanks_edit.py` vérifie:
1. Le traitement correct des données valides
2. La détection des phrases manquantes
3. La détection des mots manquants
4. La détection des phrases sans trous
5. La détection d'un nombre insuffisant de mots pour tous les trous

## Implémentation

Pour implémenter cette correction:

1. Localisez dans `app.py` la section de traitement POST de la route `edit_exercise`.
2. Trouvez le bloc qui commence par `else: # Gestion générique pour tous les autres types d'exercices`.
3. Juste avant ce bloc, insérez le code de traitement spécifique pour "fill_in_blanks" fourni ci-dessus.
4. Testez la modification en éditant un exercice "fill_in_blanks" existant.

Cette correction garantira que les modifications apportées aux phrases et aux mots lors de l'édition d'un exercice "fill_in_blanks" seront correctement sauvegardées dans la base de données.
