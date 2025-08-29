# Documentation : Correction des boutons d'upload d'image dupliqués

## Problème identifié

Plusieurs templates d'édition d'exercices contenaient des sections dupliquées pour l'upload d'images, ce qui entraînait l'affichage de plusieurs boutons d'upload sur une même page. Cette duplication causait de la confusion pour les utilisateurs et pouvait entraîner des comportements incohérents.

Templates concernés :
- `word_placement_edit.html`
- `legend_edit.html`
- `image_labeling_edit.html`
- `qcm_edit.html`
- `underline_words_edit.html`
- `qcm_multichoix_edit.html`

## Solution implémentée

### 1. Centralisation de l'interface d'upload d'image

La solution consiste à centraliser l'interface d'upload d'image dans le template parent `edit_exercise.html`, qui est maintenant utilisé comme base pour tous les templates d'édition d'exercices.

### 2. Modifications apportées aux templates

Pour chaque template d'édition d'exercice :

1. **Modification de l'héritage de template** :
   - Changement de `{% extends "base.html" %}` à `{% extends "edit_exercise.html" %}`

2. **Suppression des sections dupliquées** :
   - Suppression des blocs HTML et JavaScript liés à l'upload d'image qui étaient dupliqués
   - Conservation uniquement des éléments spécifiques à chaque type d'exercice

3. **Adaptation des blocs de contenu** :
   - Utilisation de `{% block exercise_content %}` au lieu de `{% block content %}` pour s'adapter à la structure du template parent

### 3. Avantages de cette approche

- **Interface utilisateur cohérente** : Un seul bouton d'upload d'image par page
- **Réduction de la duplication de code** : Le code d'upload d'image est maintenu à un seul endroit
- **Maintenance simplifiée** : Les modifications futures du système d'upload d'image ne nécessiteront des changements qu'à un seul endroit
- **Expérience utilisateur améliorée** : Clarté sur la façon d'ajouter une image à un exercice

## Structure actuelle des templates

```
edit_exercise.html (template parent)
├── Interface centralisée d'upload d'image
├── Bloc pour le contenu spécifique à chaque exercice
└── Templates enfants
    ├── word_placement_edit.html
    ├── legend_edit.html
    ├── image_labeling_edit.html
    ├── qcm_edit.html
    ├── underline_words_edit.html
    └── qcm_multichoix_edit.html
```

## Notes techniques

- Les templates enfants utilisent maintenant `{{ super() }}` dans leur bloc `{% block scripts %}` pour conserver les scripts JavaScript du template parent.
- Certaines erreurs de lint persistent dans `legend_edit.html` en raison du mélange de code JavaScript et de balises Jinja2, mais ces erreurs n'affectent pas le fonctionnement du code.
- La structure des données et la logique de traitement des exercices restent inchangées, seule l'interface utilisateur a été modifiée.

## Recommandations pour le développement futur

- Envisager de refactoriser davantage le code JavaScript dans les templates pour réduire les erreurs de lint
- Standardiser l'approche d'upload d'image pour tous les types d'exercices
- Ajouter des validations côté client pour les types et tailles d'images acceptés
