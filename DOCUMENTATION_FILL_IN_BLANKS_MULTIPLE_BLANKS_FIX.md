# Documentation: Correction du scoring pour exercices "Texte à trous" avec plusieurs blancs par ligne

## Problème identifié

Le système de scoring des exercices de type "texte à trous" (fill_in_blanks) ne fonctionne pas correctement lorsqu'une phrase contient plusieurs blancs à remplir. Le problème se manifeste par:

1. Un scoring incorrect lorsqu'une phrase contient plusieurs blancs à remplir
2. Une incohérence entre le comportement des exercices "texte à trous" et "mots à placer" (word_placement)

## Analyse technique

Après analyse du code, deux problèmes principaux ont été identifiés:

1. **Double comptage des blancs**: Le code comptait les blancs à la fois dans `content['text']` et `content['sentences']` pour le même exercice, créant un double comptage quand les deux champs existaient.

2. **Traitement des réponses par ligne et non par blanc**: Le système ne traitait pas correctement les réponses individuelles pour chaque blanc dans une même phrase.

## Solution implémentée

La solution consiste en deux corrections principales:

### 1. Correction du comptage des blancs

```python
# AVANT (problème de double comptage)
if 'text' in content:
    text_blanks = content['text'].count('___')
    total_blanks_in_content += text_blanks
if 'sentences' in content:
    sentences_blanks = sum(s.count('___') for s in content['sentences'])
    total_blanks_in_content += sentences_blanks
```

```python
# APRÈS (correction avec priorité)
if 'sentences' in content:
    sentences_blanks = sum(s.count('___') for s in content['sentences'])
    total_blanks_in_content = sentences_blanks
    # Log détaillé pour chaque phrase et ses blancs
    for i, sentence in enumerate(content['sentences']):
        blanks_in_sentence = sentence.count('___')
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
elif 'text' in content:
    text_blanks = content['text'].count('___')
    total_blanks_in_content = text_blanks
```

### 2. Fonction de localisation précise des blancs

Une nouvelle fonction `get_blank_location` a été ajoutée pour déterminer précisément à quelle phrase et à quelle position dans cette phrase correspond un indice global de blanc:

```python
def get_blank_location(global_blank_index, sentences):
    """Détermine à quelle phrase et à quel indice dans cette phrase correspond un indice global de blanc"""
    blank_count = 0
    for idx, sentence in enumerate(sentences):
        blanks_in_sentence = sentence.count('___')
        if blank_count <= global_blank_index < blank_count + blanks_in_sentence:
            # Calculer l'indice local du blanc dans cette phrase
            local_blank_index = global_blank_index - blank_count
            return idx, local_blank_index
        blank_count += blanks_in_sentence
    return -1, -1
```

### 3. Traitement correct des réponses par blanc individuel

```python
# Traitement de chaque blanc individuellement
for i in range(total_blanks):
    # Récupérer la réponse de l'utilisateur pour ce blanc
    user_answer = request.form.get(f'answer_{i}', '').strip()
    
    # Récupérer la réponse correcte correspondante
    correct_answer = correct_answers[i] if i < len(correct_answers) else ''
    
    # Déterminer l'emplacement précis du blanc
    sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i} est dans la phrase {sentence_index}, position locale {local_blank_index}")
    
    # Vérifier si la réponse est correcte (insensible à la casse)
    is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
    
    if is_correct:
        correct_blanks += 1
```

## Tests effectués

Plusieurs scénarios de test ont été créés pour valider la correction:

1. **Test avec plusieurs blancs dans une même ligne**:
   - Exemple: "Le ___ mange une ___ dans le jardin."
   - Résultat: Chaque blanc est compté et évalué individuellement

2. **Test avec réponses partiellement correctes**:
   - Certaines réponses correctes, d'autres incorrectes
   - Résultat: Score proportionnel au nombre de réponses correctes

3. **Test avec mots répétés**:
   - Plusieurs blancs à remplir avec le même mot
   - Résultat: Chaque instance est évaluée correctement

## Scripts créés

1. `get_blank_location.py`: Fonction utilitaire pour localiser précisément les blancs dans les phrases
2. `fix_fill_in_blanks_multiple.py`: Script d'application automatique de la correction
3. `test_fill_in_blanks_multiple.py`: Tests de validation de la correction

## Comment appliquer la correction

1. Exécuter le script d'application:
   ```
   python fix_fill_in_blanks_multiple.py
   ```

2. Le script:
   - Crée une sauvegarde du fichier app.py actuel
   - Identifie la section de code à modifier
   - Applique la correction en intégrant la fonction `get_blank_location`
   - Enregistre le fichier modifié

3. Vérifier la correction:
   ```
   python test_fill_in_blanks_multiple.py
   ```

## Résultat attendu

Après application de la correction:

1. Les exercices "texte à trous" avec plusieurs blancs dans une même ligne fonctionnent correctement
2. Le scoring est cohérent avec celui des exercices "mots à placer"
3. Les logs détaillés permettent de suivre le traitement de chaque blanc individuellement

## Recommandations supplémentaires

1. Ajouter des logs détaillés pour faciliter le débogage futur
2. Envisager d'unifier la logique de scoring entre les différents types d'exercices
3. Implémenter des tests unitaires automatisés pour ces fonctionnalités critiques
