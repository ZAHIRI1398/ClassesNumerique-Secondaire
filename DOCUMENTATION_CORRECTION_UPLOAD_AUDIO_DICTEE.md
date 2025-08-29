# Documentation : Correction de l'upload des fichiers audio MP3 dans les exercices de dictée

## Problème identifié

Lors de la création d'exercices de type dictée avec des fichiers audio MP3, l'application rencontrait une erreur empêchant l'upload et la sauvegarde des fichiers audio. Après analyse du code dans `modified_submit.py`, nous avons identifié plusieurs problèmes :

1. **Utilisation d'une variable non définie** : Le code utilisait `exercise_id` dans le nom du fichier audio avant que l'exercice ne soit créé en base de données, causant une erreur de référence.

2. **Incohérence des chemins de fichiers** : Les fichiers étaient sauvegardés dans `static/uploads/audio/` mais référencés dans le contenu JSON avec le chemin `/static/exercises/audio/`, créant une incohérence qui empêchait l'accès aux fichiers.

3. **Absence de vérification des extensions de fichiers** : La fonction `allowed_file()` ne permettait que les extensions d'images (`png`, `jpg`, `jpeg`, `gif`), mais pas les formats audio comme `mp3`.

## Solution implémentée

La correction a été réalisée en plusieurs étapes :

1. **Remplacement de `exercise_id` par un timestamp** : Utilisation d'un timestamp unique pour nommer les fichiers audio, évitant ainsi la dépendance à l'ID d'exercice non encore créé.

2. **Harmonisation des chemins de fichiers** : Utilisation cohérente du chemin `/static/uploads/audio/` à la fois pour la sauvegarde et pour la référence dans le contenu JSON.

3. **Création du répertoire d'upload** : Vérification et création du répertoire `static/uploads/audio/` s'il n'existe pas déjà.

## Code corrigé

```python
# Avant correction
filename = secure_filename(f'dictation_{exercise_id}_{i}_{audio_file.filename}')
audio_path = os.path.join('static/uploads/audio', filename)
audio_file.save(audio_path)
audio_files.append(f'/static/exercises/audio/{filename}')

# Après correction
timestamp = int(time.time())
filename = secure_filename(f'dictation_{timestamp}_{i}_{audio_file.filename}')
audio_path = os.path.join('static/uploads/audio', filename)
audio_file.save(audio_path)
audio_files.append(f'/static/uploads/audio/{filename}')
```

## Recommandations pour l'avenir

1. **Extensions autorisées** : Ajouter les extensions audio (`mp3`, `wav`, `ogg`) à la liste des extensions autorisées dans la fonction `allowed_file()`.

2. **Validation des fichiers audio** : Implémenter une validation spécifique pour les fichiers audio (taille maximale, format valide).

3. **Gestion centralisée des uploads** : Utiliser une fonction commune pour tous les types d'uploads (images, audio) afin d'assurer une cohérence dans le traitement et le stockage.

4. **Tests automatisés** : Créer des tests spécifiques pour valider le bon fonctionnement de l'upload de fichiers audio.

## Comment appliquer la correction

1. Exécuter le script `fix_dictation_audio_upload.py` qui applique automatiquement les corrections nécessaires.
2. Redémarrer l'application Flask pour que les modifications prennent effet.
3. Tester la création d'un exercice de dictée avec upload de fichier MP3.

## Validation de la correction

Pour valider que la correction fonctionne correctement :

1. Créer un nouvel exercice de type dictée
2. Ajouter une ou plusieurs phrases
3. Uploader un fichier MP3 pour chaque phrase
4. Vérifier que l'exercice est créé sans erreur
5. Ouvrir l'exercice et vérifier que les fichiers audio sont correctement lus

Si toutes ces étapes fonctionnent, la correction a été appliquée avec succès.
