#!/usr/bin/env python3
"""
Script pour corriger le problème de scoring des exercices "texte à trous" 
avec plusieurs blancs dans une ligne.
"""

from flask import current_app
import json
import logging

def fix_fill_in_blanks_scoring():
    """
    Fonction pour corriger le problème de scoring des exercices "texte à trous"
    avec plusieurs blancs dans une ligne.
    
    Le problème est que lorsqu'une phrase contient plusieurs blancs, le système
    ne compte pas correctement les réponses pour chaque blanc individuel.
    
    Cette correction s'assure que:
    1. Les blancs sont correctement comptés dans chaque phrase
    2. Les réponses utilisateur sont correctement récupérées pour chaque blanc
    3. La comparaison est faite correctement entre les réponses utilisateur et les réponses attendues
    """
    print("Correction du problème de scoring des exercices 'texte à trous' avec plusieurs blancs")
    
    # Voici le code corrigé qui devrait être intégré dans app.py
    # dans la section de traitement des exercices fill_in_blanks
    
    """
    # Exemple de code corrigé pour app.py
    
    elif exercise.exercise_type == 'fill_in_blanks':
        content = json.loads(exercise.content)
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Processing fill_in_blanks exercise {exercise_id}")
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Form data: {dict(request.form)}")
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Exercise content keys: {list(content.keys())}")
        
        # Compter le nombre réel de blancs dans le contenu
        total_blanks_in_content = 0
        
        # CORRECTION: Utiliser if/elif au lieu de if/if pour éviter le double comptage
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
            
            # Log détaillé pour chaque phrase et ses blancs
            for i, sentence in enumerate(content['sentences']):
                blanks_in_sentence = sentence.count('___')
                current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' détecté: {text_blanks} blanks dans text")
        
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Total blancs trouvés dans le contenu: {total_blanks_in_content}")
        
        # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
        correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        if not correct_answers:
            current_app.logger.error(f"[FILL_IN_BLANKS_DEBUG] No correct answers found in exercise content")
            flash('Erreur: aucune réponse correcte trouvée dans l\'exercice.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))
        
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Found {len(correct_answers)} correct answers: {correct_answers}")
        
        # Utiliser le nombre réel de blancs trouvés dans le contenu
        total_blanks = max(total_blanks_in_content, len(correct_answers))
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Using total_blanks = {total_blanks}")
        
        correct_blanks = 0
        feedback_details = []
        user_answers_data = {}
        
        # CORRECTION: Vérifier chaque blanc individuellement
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total")
        for i in range(total_blanks):
            # Récupérer la réponse de l'utilisateur pour ce blanc
            user_answer = request.form.get(f'answer_{i}', '').strip()
            
            # Récupérer la réponse correcte correspondante
            correct_answer = correct_answers[i] if i < len(correct_answers) else ''
            
            current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i}:")
            current_app.logger.info(f"  - Réponse étudiant (answer_{i}): {user_answer}")
            current_app.logger.info(f"  - Réponse attendue: {correct_answer}")
            
            # Vérifier si la réponse est correcte (insensible à la casse)
            is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
            
            if is_correct:
                correct_blanks += 1
                feedback_details.append({
                    'blank': i,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': True,
                    'message': 'Correct!'
                })
            else:
                feedback_details.append({
                    'blank': i,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': False,
                    'message': f'Incorrect. La réponse correcte était: {correct_answer}'
                })
            
            # Sauvegarder les réponses utilisateur
            user_answers_data[f'answer_{i}'] = user_answer
        
        # Calculer le score final basé sur le nombre réel de blancs
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        
        current_app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Score final: {score}% ({correct_blanks}/{total_blanks})")
        
        feedback_summary = {
            'score': score,
            'correct_count': correct_blanks,
            'total_count': total_blanks,
            'details': feedback_details
        }
        
        # Pour fill_in_blanks, on utilise le score calculé
        answers = user_answers_data
    """
    
    print("\nPour appliquer cette correction:")
    print("1. Ouvrez app.py")
    print("2. Recherchez la section de traitement des exercices 'fill_in_blanks'")
    print("3. Assurez-vous que le comptage des blancs utilise if/elif au lieu de if/if")
    print("4. Vérifiez que chaque réponse est traitée individuellement avec answer_0, answer_1, etc.")
    print("5. Assurez-vous que le score est calculé correctement avec (correct_blanks / total_blanks) * 100")
    
    print("\nCette correction devrait résoudre le problème de scoring pour les exercices")
    print("'texte à trous' avec plusieurs blancs dans une ligne.")

if __name__ == "__main__":
    fix_fill_in_blanks_scoring()
