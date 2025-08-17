#!/usr/bin/env python3
"""
Script pour appliquer la correction complète du scoring fill_in_blanks dans app.py
Ce script:
1. Désactive la première implémentation avec un pass
2. Ajoute la deuxième implémentation complète si elle est manquante
3. Crée une sauvegarde avant toute modification
"""

import re
import os
import sys
import shutil
import datetime

def create_backup():
    """Crée une sauvegarde de app.py"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"app.py.bak.{timestamp}"
    
    try:
        shutil.copy2("app.py", backup_file)
        print(f"Sauvegarde créée: {backup_file}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {e}")
        return False

def disable_first_implementation():
    """Désactive la première implémentation du scoring fill_in_blanks"""
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Rechercher le bloc de la première implémentation
        pattern = r"(elif exercise\.exercise_type == 'fill_in_blanks':)([^\n]*\n)(?:    [^\n]*\n)*?(?=    elif)"
        
        # Remplacer par un commentaire et un pass
        replacement = r"\1\n    # Cette implémentation a été désactivée car elle est en conflit avec l'implémentation plus complète\n    # Voir lignes ~3415-3510 pour l'implémentation active.\n    pass\n\n"
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content == content:
            print("Aucune modification n'a été apportée pour la première implémentation.")
            print("Soit elle est déjà désactivée, soit le pattern n'a pas été trouvé.")
            return False
        
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_content)
            
        print("Première implémentation désactivée avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la désactivation de la première implémentation: {e}")
        return False

def add_second_implementation():
    """Ajoute la deuxième implémentation complète du scoring fill_in_blanks"""
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Vérifier si la deuxième implémentation est déjà présente
        if "# Logique de scoring pour fill_in_blanks" in content:
            print("La deuxième implémentation semble déjà être présente.")
            return False
        
        # Trouver l'endroit où ajouter la deuxième implémentation
        # Nous allons l'ajouter juste avant la section de création de tentative
        pattern = r"(# Créer une nouvelle tentative\s+# Pour drag_and_drop)"
        
        # Code de la deuxième implémentation à ajouter
        second_implementation = """        # Logique de scoring pour fill_in_blanks
        elif exercise.exercise_type == 'fill_in_blanks':
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de l'exercice fill_in_blanks ID {exercise_id}")
            content = exercise.get_content()
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Contenu de l'exercice: {content}")
            
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
            # Log détaillé pour chaque phrase et ses blancs
            if 'sentences' in content:
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            
            # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
            correct_answers = content.get('words', [])
            if not correct_answers:
                correct_answers = content.get('available_words', [])
            
            if not correct_answers:
                app.logger.error(f"[FILL_IN_BLANKS_DEBUG] No correct answers found in exercise content")
                flash('Erreur: aucune réponse correcte trouvée dans l\\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Found {len(correct_answers)} correct answers: {correct_answers}")
            
            # Utiliser le nombre réel de blancs trouvés dans le contenu
            total_blanks = max(total_blanks_in_content, len(correct_answers))
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Using total_blanks = {total_blanks}")
            
            correct_blanks = 0
            feedback_details = []
            user_answers_data = {}
            
            # Vérifier chaque blanc individuellement - Même logique que word_placement
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total")
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
                feedback_details.append({
                    'blank_index': i,
                    'user_answer': user_answer or '',
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}'
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
            answers = user_answers_data
        """
        
        # Ajouter la deuxième implémentation
        new_content = re.sub(pattern, second_implementation + "\n        " + r"\1", content)
        
        if new_content == content:
            print("Aucune modification n'a été apportée pour la deuxième implémentation.")
            print("Le pattern pour l'insertion n'a pas été trouvé.")
            return False
        
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_content)
            
        print("Deuxième implémentation ajoutée avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de la deuxième implémentation: {e}")
        return False

def modify_redirect_to_feedback():
    """Modifie la redirection pour afficher le template feedback.html"""
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Rechercher le bloc de redirection
        pattern = r"(# Rediriger vers l'exercice avec le feedback\s+)return redirect\(url_for\('view_exercise', exercise_id=exercise_id.*?\)\)"
        
        # Remplacer par une redirection vers feedback.html
        replacement = r"\1return render_template('feedback.html', exercise=exercise, attempt=attempt, answers=answers, feedback=feedback_to_save)"
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content == content:
            print("Aucune modification n'a été apportée pour la redirection.")
            print("Le pattern n'a pas été trouvé.")
            return False
        
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_content)
            
        print("Redirection modifiée avec succès pour afficher feedback.html.")
        return True
    except Exception as e:
        print(f"Erreur lors de la modification de la redirection: {e}")
        return False

def main():
    """Fonction principale"""
    print("=== Application de la correction complète du scoring fill_in_blanks ===\n")
    
    # Créer une sauvegarde
    if not create_backup():
        print("Abandon de l'opération en raison d'une erreur lors de la sauvegarde.")
        return
    
    # Désactiver la première implémentation
    disable_first_implementation()
    
    # Ajouter la deuxième implémentation
    add_second_implementation()
    
    # Modifier la redirection
    modify_redirect_to_feedback()
    
    print("\n=== Correction appliquée avec succès ===")
    print("Pour que les modifications prennent effet, vous devez redémarrer l'application Flask:")
    print("1. Arrêtez l'application Flask en cours d'exécution (Ctrl+C dans le terminal)")
    print("2. Redémarrez l'application avec 'flask run'")
    print("3. Testez l'exercice ID 6 pour vérifier que le score est maintenant correct")

if __name__ == "__main__":
    main()
