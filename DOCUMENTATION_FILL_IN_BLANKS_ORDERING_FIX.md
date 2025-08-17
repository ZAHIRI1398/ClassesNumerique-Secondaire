# Documentation: Correction du Scoring des Exercices Fill-in-Blanks de Type Rangement

## Problème
Les exercices de type "texte à trous" (fill_in_blanks) qui demandent de ranger des éléments par ordre croissant ou décroissant ne sont pas correctement évalués. Le système ne détecte pas correctement les exercices décroissants et n'évalue pas les réponses selon la logique de rangement.

## Solution
La solution consiste à:
1. Détecter si l'exercice est de type rangement (croissant ou décroissant) en analysant la description
2. Appliquer une logique d'évaluation spécifique pour les exercices de rangement
3. Maintenir la logique standard pour les autres exercices fill_in_blanks

## Modifications à apporter à app.py

### 1. Vérifier que l'import est présent
```python
from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise
```

### 2. Modifier la section de traitement des exercices fill_in_blanks
Localiser la section qui commence par:
```python
        elif exercise.exercise_type == 'fill_in_blanks':
            # Gestion des exercices Texte à trous avec la même logique que Mots à placer
```

### 3. Remplacer la section de traitement des blanks par le code suivant:
```python
            correct_blanks = 0
            feedback_details = []
            user_answers_data = {}
            
            # Vérifier si c'est un exercice de rangement par ordre
            is_ordering, ordering_type = is_ordering_exercise(exercise.description)
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Détection exercice de rangement: {is_ordering}, type: {ordering_type}")
            
            # Si c'est un exercice de rangement, utiliser la logique spécifique
            if is_ordering:
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement d'un exercice de rangement {ordering_type}")
                
                # Récupérer toutes les réponses de l'utilisateur
                user_answers_list = []
                for i in range(total_blanks):
                    user_answer = request.form.get(f'answer_{i}', '').strip()
                    user_answers_list.append(user_answer)
                    user_answers_data[f'answer_{i}'] = user_answer
                
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Réponses utilisateur: {user_answers_list}")
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Réponses correctes: {correct_answers}")
                
                # Évaluer les réponses avec la logique de rangement
                correct_count, feedback_list = evaluate_ordering_exercise(user_answers_list, correct_answers, ordering_type)
                correct_blanks = correct_count
                
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Résultat évaluation: {correct_count}/{total_blanks} corrects")
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Feedback détaillé: {feedback_list}")
                
                # Créer le feedback détaillé
                for i in range(len(user_answers_list)):
                    user_answer = user_answers_list[i] if i < len(user_answers_list) else ''
                    correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                    is_correct = feedback_list[i] if i < len(feedback_list) else False
                    
                    # Déterminer l'index de la phrase à laquelle appartient ce blanc
                    sentence_index = -1
                    local_blank_index = -1
                    if 'sentences' in content:
                        sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
                    
                    feedback_details.append({
                        'blank_index': i,
                        'user_answer': user_answer or '',
                        'correct_answer': correct_answer,
                        'is_correct': is_correct,
                        'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}',
                        'sentence_index': sentence_index,
                        'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''
                    })
            else:
                # Vérifier chaque blanc individuellement - Même logique que word_placement
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total (exercice standard)")
                for i in range(total_blanks):
                    # Récupérer la réponse de l'utilisateur pour ce blanc
                    user_answer = request.form.get(f'answer_{i}', '').strip()
                    
                    # Récupérer la réponse correcte correspondante
                    correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                    
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i}:")
                    app.logger.info(f"  - Réponse étudiant (answer_{i}): {user_answer}")
                    app.logger.info(f"  - Réponse attendue: {correct_answer}")
                    
                    # Vérifier si la réponse est correcte (insensible à la casse)
                    is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
                    if is_correct:
                        correct_blanks += 1
                    
                    # Créer le feedback pour ce blanc
                    # Déterminer l'index de la phrase à laquelle appartient ce blanc
                    sentence_index = -1
                    local_blank_index = -1
                    if 'sentences' in content:
                        sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
                        app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i} est dans la phrase {sentence_index}, position locale {local_blank_index}")
                    
                    feedback_details.append({
                        'blank_index': i,
                        'user_answer': user_answer or '',
                        'correct_answer': correct_answer,
                        'is_correct': is_correct,
                        'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}',
                        'sentence_index': sentence_index,
                        'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''
                    })
                    
                    # Sauvegarder les réponses utilisateur
                    user_answers_data[f'answer_{i}'] = user_answer
            
            # Calculer le score final basé sur le nombre réel de blancs - Exactement comme word_placement
            score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
```

## Tests
Pour tester cette modification:
1. Créer un exercice fill_in_blanks avec une description contenant "ranger par ordre croissant" ou "ranger par ordre décroissant"
2. Soumettre des réponses dans l'ordre correct et vérifier que le score est de 100%
3. Soumettre des réponses dans un ordre incorrect et vérifier que le score est inférieur à 100%

## Fichiers associés
- `analyze_fill_in_blanks_ordering.py`: Contient les fonctions de détection et d'évaluation des exercices de rangement
- `test_fill_in_blanks_ordering.py`: Tests unitaires pour valider la détection et l'évaluation des exercices de rangement
