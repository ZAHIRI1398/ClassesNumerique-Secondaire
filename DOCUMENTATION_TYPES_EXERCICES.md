# Documentation des Types d'Exercices

Ce document décrit la structure et l'implémentation de chaque type d'exercice disponible dans la plateforme Classes Numériques.

## 1. QCM (Questionnaire à Choix Multiples)

### Structure du contenu JSON
```json
{
    "image": "/static/uploads/qcm/example.png",
    "questions": [
        {
            "text": "Question 1?",
            "choices": ["Option 1", "Option 2", "Option 3"],
            "correct_answer": 0
        },
        {
            "text": "Question 2?",
            "choices": ["Option 1", "Option 2", "Option 3"],
            "correct_answer": 1
        }
    ]
}
```

### Propriétés
- `image`: Chemin vers l'image d'illustration (optionnel)
- `questions`: Tableau des questions
  - `text`: Texte de la question
  - `choices`: Tableau des options de réponse
  - `correct_answer`: Index de la réponse correcte (commence à 0)

## 2. QCM Multichoix

### Structure du contenu JSON
```json
{
    "image": "/static/uploads/qcm_multichoix/example.png",
    "instructions": "Cochez toutes les réponses correctes pour chaque question.",
    "questions": [
        {
            "text": "Question 1?",
            "choices": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answers": [0, 2]
        },
        {
            "text": "Question 2?",
            "choices": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answers": [1, 3]
        }
    ]
}
```

### Propriétés
- `image`: Chemin vers l'image d'illustration (optionnel)
- `instructions`: Instructions pour l'exercice
- `questions`: Tableau des questions
  - `text`: Texte de la question
  - `choices`: Tableau des options de réponse
  - `correct_answers`: Tableau des index des réponses correctes (commence à 0)

## 3. Texte à trous (Fill in Blanks)

### Structure du contenu JSON
```json
{
    "image": "/static/uploads/fill_in_blanks/example.png",
    "sentences": [
        {"text": "Le chat ___ sur le canapé.", "answer": "dort"},
        {"text": "Paris est la capitale de la ___.", "answer": "France"}
    ],
    "available_words": ["dort", "France", "mange", "Allemagne"]
}
```

### Propriétés
- `image`: Chemin vers l'image d'illustration (optionnel)
- `sentences`: Tableau des phrases à compléter
  - `text`: Texte avec des blancs (représentés par `___`)
  - `answer`: Réponse correcte pour le blanc
- `available_words`: Liste des mots disponibles pour remplir les blancs (optionnel)

## 4. Association de paires

### Structure du contenu JSON
```json
{
    "image": "/static/uploads/pairs/example.png",
    "left_items": ["Item 1", "Item 2", "Item 3"],
    "right_items": ["Correspondance 1", "Correspondance 2", "Correspondance 3"],
    "correct_pairs": [[0, 0], [1, 1], [2, 2]]
}
```

### Propriétés
- `image`: Chemin vers l'image d'illustration (optionnel)
- `left_items`: Tableau des éléments de la colonne de gauche
- `right_items`: Tableau des éléments de la colonne de droite
- `correct_pairs`: Tableau des paires correctes sous forme [index_gauche, index_droite]

## 5. Mots à placer

### Structure du contenu JSON
```json
{
    "image": "/static/uploads/word_placement/example.png",
    "instructions": "Faites glisser les mots dans les bonnes phrases.",
    "sentences": [
        "Le chat ___ sur le canapé.",
        "Les enfants ___ dans le jardin."
    ],
    "words": ["dort", "jouent"],
    "answers": [
        {"sentence_index": 0, "word_index": 0},
        {"sentence_index": 1, "word_index": 1}
    ]
}
```

### Propriétés
- `image`: Chemin vers l'image d'illustration (optionnel)
- `instructions`: Instructions pour l'exercice
- `sentences`: Tableau des phrases avec des blancs (représentés par `___`)
- `words`: Tableau des mots à placer
- `answers`: Tableau des réponses correctes
  - `sentence_index`: Index de la phrase (commence à 0)
  - `word_index`: Index du mot à placer (commence à 0)

## 6. Souligner les mots

### Structure du contenu JSON
```json
{
    "image": "/static/uploads/underline_words/example.png",
    "instructions": "Soulignez tous les verbes dans les phrases suivantes.",
    "sentences": [
        {"text": "Le chat dort sur le canapé.", "words_to_underline": [2]},
        {"text": "Les enfants jouent dans le jardin.", "words_to_underline": [2]}
    ]
}
```

### Propriétés
- `image`: Chemin vers l'image d'illustration (optionnel)
- `instructions`: Instructions pour l'exercice
- `sentences`: Tableau des phrases
  - `text`: Texte de la phrase
  - `words_to_underline`: Tableau des index des mots à souligner (commence à 0)

## 7. Glisser-déposer

### Structure du contenu JSON
```json
{
    "image": "/static/uploads/drag_drop/example.png",
    "draggable_items": ["Item 1", "Item 2", "Item 3", "Item 4"],
    "drop_zones": ["Zone 1", "Zone 2", "Zone 3", "Zone 4"],
    "correct_order": [2, 0, 3, 1]
}
```

### Propriétés
- `image`: Chemin vers l'image d'illustration (optionnel)
- `draggable_items`: Tableau des éléments à glisser
- `drop_zones`: Tableau des zones de dépôt
- `correct_order`: Tableau des index des éléments dans l'ordre correct

## 8. Cartes mémoire

### Structure du contenu JSON
```json
{
    "image": "/static/uploads/flashcards/example.png",
    "instructions": "Cliquez sur une carte pour voir sa traduction.",
    "cards": [
        {"front": "Maison", "back": "House"},
        {"front": "Voiture", "back": "Car"},
        {"front": "École", "back": "School"}
    ]
}
```

### Propriétés
- `image`: Chemin vers l'image d'illustration (optionnel)
- `instructions`: Instructions pour l'exercice
- `cards`: Tableau des cartes
  - `front`: Texte sur le recto de la carte
  - `back`: Texte sur le verso de la carte

## Bonnes pratiques pour les chemins d'images

Pour tous les types d'exercices, les chemins d'images doivent suivre ces conventions:

1. Toujours utiliser le préfixe `/static/uploads/` pour les chemins d'images
2. Organiser les images par type d'exercice (ex: `/static/uploads/qcm/`, `/static/uploads/fill_in_blanks/`)
3. Utiliser des noms de fichiers descriptifs et sans espaces
4. Synchroniser le chemin d'image dans `exercise.image_path` et dans le contenu JSON (`content.image`)

Exemple:
```python
exercise = Exercise(
    title="Mon exercice QCM",
    exercise_type="qcm",
    image_path="/static/uploads/qcm/mon_image.png",
    content=json.dumps({
        "image": "/static/uploads/qcm/mon_image.png",
        # autres propriétés...
    })
)
```

## Création d'exercices via script

Pour créer des exercices programmatiquement, utilisez les scripts suivants:
- `init_exercises.py`: Crée les exercices de base (QCM, texte à trous, association de paires, glisser-déposer)
- `create_additional_exercises.py`: Crée les exercices supplémentaires (QCM multichoix, mots à placer, souligner les mots, cartes mémoire)

Ces scripts créent également automatiquement les images nécessaires dans les répertoires appropriés.
