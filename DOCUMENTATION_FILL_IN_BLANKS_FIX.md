# Documentation : Correction des problèmes de scoring dans les exercices "Texte à trous"

## Problèmes identifiés

### 1. Absence du champ 'answers' dans les exercices "Texte à trous"

Les exercices de type "texte à trous" (fill_in_blanks) ne possédaient pas le champ `answers` dans leur structure JSON, contrairement aux exercices "Mots à placer" (word_placement). Ce champ est essentiel pour une évaluation correcte des réponses des utilisateurs.

### 2. Risque de double comptage des blancs

Lorsqu'un exercice contient à la fois les champs `sentences` et `text`, il existe un risque de double comptage des blancs, ce qui peut fausser le calcul du score. Par exemple, un exercice avec 2 blancs pourrait être compté comme ayant 4 blancs (2 dans `text` + 2 dans `sentences`).

### 3. Incohérence entre le nombre de blancs et le nombre de réponses attendues

Certains exercices présentaient une incohérence entre le nombre de blancs (`___`) dans le contenu et le nombre de réponses attendues dans les champs `words` ou `available_words`.

## Solutions appliquées

### 1. Ajout du champ 'answers' manquant

Un script de diagnostic et de correction (`test_fill_in_blanks_diagnostic.py`) a été créé pour analyser tous les exercices de type "texte à trous" et ajouter le champ `answers` manquant. Ce champ est généré à partir des mots disponibles (`words` ou `available_words`) et ajusté pour correspondre au nombre de blancs dans le contenu.

```json
// Avant correction
{
  "sentences": ["Un triangle qui possède un angle droit et deux cotés isometriques est un triangle ___ ___"],
  "words": ["isocèle", "rectangle"]
}

// Après correction
{
  "sentences": ["Un triangle qui possède un angle droit et deux cotés isometriques est un triangle ___ ___"],
  "words": ["isocèle", "rectangle"],
  "answers": ["isocèle", "rectangle"]
}
```

### 2. Correction de la logique de comptage des blancs

La logique de comptage des blancs a été modifiée pour éviter le double comptage lorsque les deux champs `sentences` et `text` sont présents dans le même exercice. La priorité est donnée au champ `sentences` :

```python
# AVANT (problème de double comptage)
if 'text' in content:
    text_blanks = content['text'].count('___')
    total_blanks_in_content += text_blanks
if 'sentences' in content:
    sentences_blanks = sum(s.count('___') for s in content['sentences'])
    total_blanks_in_content += sentences_blanks

# APRÈS (correction avec priorité)
if 'sentences' in content:
    sentences_blanks = sum(s.count('___') for s in content['sentences'])
    total_blanks_in_content = sentences_blanks
elif 'text' in content:
    text_blanks = content['text'].count('___')
    total_blanks_in_content = text_blanks
```

### 3. Cohérence entre blancs et réponses

Le script de correction assure la cohérence entre le nombre de blancs et le nombre de réponses attendues en ajustant le champ `answers` :

- Si le nombre de réponses est inférieur au nombre de blancs, des réponses supplémentaires sont ajoutées
- Si le nombre de réponses est supérieur au nombre de blancs, les réponses excédentaires sont tronquées

## Logique de scoring corrigée

La logique de scoring pour les exercices "Texte à trous" utilise maintenant la même approche robuste que celle des exercices "Mots à placer" :

1. Compter les blancs (`___`) dans le contenu en priorisant `sentences` sur `text`
2. Récupérer les réponses correctes depuis le champ `answers` (nouvellement ajouté)
3. Utiliser le maximum entre le nombre de blancs et le nombre de réponses comme dénominateur pour le calcul du score
4. Calculer le score comme : `(correct_blanks / total_blanks) * 100`

```python
# Logique de scoring robuste
total_blanks_in_content = 0
if 'sentences' in content:
    sentences_blanks = sum(s.count('___') for s in content['sentences'])
    total_blanks_in_content = sentences_blanks
elif 'text' in content:
    text_blanks = content['text'].count('___')
    total_blanks_in_content = text_blanks

# Utiliser le maximum entre blancs et réponses
total_blanks = max(total_blanks_in_content, len(content['answers']))
score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
```

## Recommandations pour la création d'exercices "Texte à trous"

Pour assurer un scoring correct des exercices "Texte à trous", suivez ces bonnes pratiques :

1. **Toujours inclure le champ `answers`** avec les réponses attendues dans l'ordre correspondant aux blancs
2. **Utiliser soit `sentences` soit `text`**, mais éviter d'utiliser les deux dans le même exercice
3. **Assurer la cohérence** entre le nombre de blancs et le nombre de réponses attendues
4. **Tester l'exercice** avec différentes combinaisons de réponses pour vérifier le scoring

## Scripts de diagnostic et de correction

Deux scripts ont été créés pour diagnostiquer et corriger les problèmes de structure dans les exercices "Texte à trous" :

1. **`test_fill_in_blanks_diagnostic.py`** : Analyse tous les exercices "Texte à trous" et affiche leur structure, le nombre de blancs, les réponses attendues, et les tentatives récentes.

2. **`test_fill_in_blanks_scoring_after_fix.py`** : Vérifie que les corrections ont été appliquées correctement et que le scoring fonctionne comme prévu.

Pour exécuter le diagnostic et appliquer les corrections :

```bash
python test_fill_in_blanks_diagnostic.py fix
```
