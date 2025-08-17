"""
Ce fichier contient la version modifiée de la fonction de traitement des exercices fill_in_blanks
avec la logique de détection et d'évaluation des exercices de rangement intégrée.

Pour l'intégrer dans app.py:
1. Ajouter l'import: from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise
2. Remplacer la section de traitement des exercices fill_in_blanks par ce code
"""

def process_fill_in_blanks_exercise(exercise, exercise_id, request):
    """
    Fonction de traitement des exercices fill_in_blanks avec support pour les exercices de rangement.
    À intégrer dans app.py.
    """
    # Gestion des exercices Texte à trous avec la même logique que Mots à placer
    content = json.loads(exercise.content)
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Processing fill_in_blanks exercise {exercise_id}")
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Form data: {dict(request.form)}")
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Exercise content keys: {list(content.keys())}")
    
    # Compter le nombre réel de blancs dans le contenu
    total_blanks_in_content = 0
    
    # Analyser le format de l'exercice et compter les blancs réels
    # CORRECTION: Éviter le double comptage entre 'text' et 'sentences'
    # Priorité à 'sentences' s'il existe, sinon utiliser 'text'
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        total_blanks_in_content = sentences_blanks
        app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
        # Log détaillé pour chaque phrase et ses blancs
        for i, sentence in enumerate(content['sentences']):
            blanks_in_sentence = sentence.count('___')
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
    elif 'text' in content:
        text_blanks = content['text'].count('___')
        total_blanks_in_content = text_blanks
        app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' détecté: {text_blanks} blancs dans text")
    
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Total blancs trouvés dans le contenu: {total_blanks_in_content}")
    
    # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
    correct_answers = content.get('words', [])
    if not correct_answers:
        correct_answers = content.get('available_words', [])
    
    if not correct_answers:
        app.logger.error(f"[FILL_IN_BLANKS_DEBUG] No correct answers found in exercise content")
        flash('Erreur: aucune réponse correcte trouvée dans l\'exercice.', 'error')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))
    
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Found {len(correct_answers)} correct answers: {correct_answers}")
    
    # Utiliser le nombre réel de blancs trouvés dans le contenu
    total_blanks = max(total_blanks_in_content, len(correct_answers))
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Using total_blanks = {total_blanks}")
    
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
        # Logique standard pour les exercices non-rangement
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
    
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Score final: {score}% ({correct_blanks}/{total_blanks})")
    
    feedback_summary = {
        'score': score,
        'correct_blanks': correct_blanks,
        'total_blanks': total_blanks,
        'details': feedback_details
    }
    
    # Pour fill_in_blanks, on utilise le score calculé
    return feedback_summary, user_answers_data
