"""
Ce fichier contient le patch à appliquer pour intégrer la logique de détection et d'évaluation
des exercices de rangement dans app.py.

Instructions d'intégration:
1. Ajouter l'import: from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise
2. Remplacer la section de traitement des blanks dans la fonction submit_exercise pour les exercices fill_in_blanks
   par le code ci-dessous.
"""

# Code à insérer après la ligne "user_answers_data = {}" (ligne ~3490)
"""
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
                # Logique standard pour les exercices non-rangement
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total (exercice standard)")
"""

# Remplacer la boucle existante par cette condition
"""
                # Cette section est exécutée uniquement pour les exercices non-rangement
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
"""
