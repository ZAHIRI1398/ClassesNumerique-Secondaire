# Documentation : Correction de l'affichage des réponses par défaut dans les exercices "Texte à trous"

## Problème initial

Les exercices de type "Texte à trous" (fill_in_blanks) affichaient automatiquement les réponses précédentes de l'utilisateur dans les champs de saisie, même lorsque l'exercice n'avait pas encore été soumis. Ce comportement n'était pas souhaitable car :

1. Il pouvait créer de la confusion pour les utilisateurs
2. Il permettait de voir les réponses précédentes sans avoir à les ressaisir
3. Il ne correspondait pas au comportement attendu où les champs devraient être vides lors de la première visite

## Cause racine identifiée

Après analyse du code, deux éléments ont été identifiés comme causes du problème :

1. **Dans la fonction `view_exercise` (app.py)** :
   - Les réponses utilisateur étaient récupérées dès qu'une tentative existait, sans vérifier si cette tentative avait été effectivement soumise (présence de feedback)
   - Ces réponses étaient ensuite passées au template via la variable `user_answers`

2. **Dans le template `fill_in_blanks.html`** :
   - Les champs de saisie utilisaient systématiquement l'attribut `value="{{ user_answers.get('answer_' ~ blank_counter[0], '') }}"` sans condition
   - Cela affichait les réponses dès que `user_answers` contenait des valeurs

## Solution implémentée

La correction a été réalisée en deux parties :

### 1. Modification de la fonction `view_exercise` dans app.py

Nous avons ajouté une vérification pour s'assurer que les réponses utilisateur ne sont récupérées et passées au template que si l'exercice a été effectivement soumis :

```python
# Si une tentative existe, récupérer les réponses de l'utilisateur
# mais seulement si l'exercice a été soumis (pour éviter d'afficher les réponses par défaut)
show_answers = False
if attempt:
    print(f'[VIEW_EXERCISE_DEBUG] Found attempt ID: {attempt.id}')
    # Vérifier si l'exercice a été soumis (présence de feedback)
    if attempt.feedback and attempt.feedback.strip():
        show_answers = True
        try:
            # Récupérer les réponses de l'utilisateur depuis le feedback
            feedback = json.loads(attempt.feedback) if attempt.feedback else []
            for item in feedback:
                if 'student_answer' in item and 'blank_index' in item:
                    user_answers[f'answer_{item["blank_index"]}'] = item['student_answer']
                elif 'student_answer' in item:
                    # Pour les autres formats de feedback
                    blank_counter = len(user_answers)
                    user_answers[f'answer_{blank_counter}'] = item['student_answer']
            print(f'[VIEW_EXERCISE_DEBUG] User answers: {user_answers}')
        except Exception as e:
            app.logger.error(f'Error parsing attempt feedback: {str(e)}')
            print(f'[VIEW_EXERCISE_DEBUG] Error parsing feedback: {str(e)}')
    else:
        print(f'[VIEW_EXERCISE_DEBUG] Attempt exists but no feedback, not showing answers')
        # Réinitialiser user_answers pour éviter d'afficher des réponses par défaut
        user_answers = {}
```

Une nouvelle variable `show_answers` a été ajoutée et passée au template :

```python
return render_template(template,
                    exercise=exercise,
                    attempt=attempt,
                    content=content,
                    progress=progress,
                    course=course,
                    user_answers=user_answers,
                    show_answers=show_answers)
```

### 2. Modification du template fill_in_blanks.html

Le template a été modifié pour n'afficher les réponses utilisateur que si `show_answers` est vrai :

```html
<input type="text" 
       class="blank-input d-inline-block mx-1" 
       name="answer_{{ blank_counter[0] }}" 
       required 
       placeholder="____"
       {% if show_answers %}
       value="{{ user_answers.get('answer_' ~ blank_counter[0], '') }}"
       {% endif %}
       style="width: auto; min-width: 80px; max-width: 150px;">
```

Cette modification a été appliquée aux deux formats d'exercices supportés (avec `sentences` ou avec `text`).

## Tests effectués

Un script de test `test_fill_in_blanks_display_fix.py` a été créé pour vérifier que la solution fonctionne correctement. Ce script teste :

1. La logique de la fonction `view_exercise` pour déterminer correctement quand `show_answers` doit être vrai ou faux
2. Le rendu du template avec et sans affichage des réponses

Les tests ont confirmé que :
- Lorsqu'une tentative existe avec feedback, les réponses sont affichées
- Lorsqu'une tentative existe sans feedback, les réponses ne sont pas affichées
- Le template n'affiche les réponses que lorsque `show_answers` est vrai

## Impact et bénéfices

Cette correction améliore l'expérience utilisateur en :
1. Évitant la confusion potentielle causée par l'affichage automatique des réponses
2. Rendant le comportement plus intuitif (champs vides par défaut)
3. Maintenant la fonctionnalité de pré-remplissage après soumission, ce qui est utile pour corriger des erreurs

## Recommandations pour le déploiement

1. Sauvegarder les fichiers modifiés avant déploiement
2. Déployer les modifications sur un environnement de test avant la production
3. Vérifier que les exercices existants fonctionnent correctement avec cette modification
4. S'assurer que les deux formats d'exercices (avec `sentences` ou avec `text`) sont correctement pris en charge

## Fichiers modifiés

- `app.py` - Modification de la fonction `view_exercise`
- `templates/exercise_types/fill_in_blanks.html` - Ajout de la condition pour l'affichage des réponses

## Auteur et date

- Auteur : Assistant IA
- Date : 16 août 2025
