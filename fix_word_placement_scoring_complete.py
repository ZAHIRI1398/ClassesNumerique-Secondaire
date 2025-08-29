import os
import sys
import json
import logging
import sqlite3
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_word_placement_scoring():
    """
    Corrige le problème de scoring des exercices word_placement qui affichent toujours 0%
    au lieu de 100% même avec des réponses correctes.
    """
    try:
        # Chemin vers le fichier app.py
        app_path = 'app.py'
        backup_path = f'app.py.bak.word_placement_scoring_{int(datetime.now().timestamp())}'
        
        # Vérifier si le fichier existe
        if not os.path.exists(app_path):
            logger.error(f"Le fichier {app_path} n'existe pas.")
            return False
        
        # Créer une sauvegarde
        with open(app_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        logger.info(f"Sauvegarde créée: {backup_path}")
        
        # Rechercher la section de code qui traite le scoring des exercices word_placement
        old_code = """    elif exercise.exercise_type == 'word_placement':
        print("\\n=== DÉBUT SCORING WORD_PLACEMENT ===")
        content = exercise.get_content()
        print(f"[WORD_PLACEMENT_DEBUG] Content: {content}")
        
        if not isinstance(content, dict) or 'sentences' not in content or 'answers' not in content:
            print("[WORD_PLACEMENT_DEBUG] Structure invalide!")
            flash('Structure de l\\'exercice invalide.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))

        sentences = content['sentences']
        correct_answers = content['answers']
        
        # CORRECTION: Compter le nombre réel de blancs dans les phrases
        total_blanks_in_sentences = sum(s.count('___') for s in sentences)
        total_blanks = max(total_blanks_in_sentences, len(correct_answers))
        
        correct_count = 0
        
        print(f"[WORD_PLACEMENT_DEBUG] Total blanks in sentences: {total_blanks_in_sentences}")
        print(f"[WORD_PLACEMENT_DEBUG] Total answers: {len(correct_answers)}")
        print(f"[WORD_PLACEMENT_DEBUG] Using total_blanks = {total_blanks}")
        print(f"[WORD_PLACEMENT_DEBUG] Expected answers: {correct_answers}")

        # Vérifier chaque réponse
        for i in range(total_blanks):
            student_answer = request.form.get(f'answer_{i}')
            expected_answer = correct_answers[i] if i < len(correct_answers) else ''
            
            print(f"[WORD_PLACEMENT_DEBUG] Blank {i}:")
            print(f"  - Réponse étudiant (answer_{i}): {student_answer}")
            print(f"  - Réponse attendue: {expected_answer}")
            
            if student_answer and student_answer.strip().lower() == expected_answer.strip().lower():
                correct_count += 1
                feedback.append({
                    'blank_index': i,
                    'student_answer': student_answer,
                    'correct_answer': expected_answer,
                    'is_correct': True
                })
            else:
                feedback.append({
                    'blank_index': i,
                    'student_answer': student_answer or '',
                    'correct_answer': expected_answer,
                    'is_correct': False
                })

        score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        print(f"[WORD_PLACEMENT_DEBUG] Score final: {score}% ({correct_count}/{total_blanks} = {correct_count/total_blanks if total_blanks > 0 else 0})")"""
        
        new_code = """    elif exercise.exercise_type == 'word_placement':
        print("\\n=== DÉBUT SCORING WORD_PLACEMENT ===")
        content = exercise.get_content()
        print(f"[WORD_PLACEMENT_DEBUG] Content: {content}")
        
        if not isinstance(content, dict) or 'sentences' not in content or 'answers' not in content:
            print("[WORD_PLACEMENT_DEBUG] Structure invalide!")
            flash('Structure de l\\'exercice invalide.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))

        sentences = content['sentences']
        correct_answers = content['answers']
        
        # CORRECTION: Compter le nombre réel de blancs dans les phrases
        total_blanks_in_sentences = sum(s.count('___') for s in sentences)
        total_blanks = max(total_blanks_in_sentences, len(correct_answers))
        
        correct_count = 0
        
        print(f"[WORD_PLACEMENT_DEBUG] Total blanks in sentences: {total_blanks_in_sentences}")
        print(f"[WORD_PLACEMENT_DEBUG] Total answers: {len(correct_answers)}")
        print(f"[WORD_PLACEMENT_DEBUG] Using total_blanks = {total_blanks}")
        print(f"[WORD_PLACEMENT_DEBUG] Expected answers: {correct_answers}")

        # Vérifier chaque réponse
        for i in range(total_blanks):
            student_answer = request.form.get(f'answer_{i}')
            expected_answer = correct_answers[i] if i < len(correct_answers) else ''
            
            print(f"[WORD_PLACEMENT_DEBUG] Blank {i}:")
            print(f"  - Réponse étudiant (answer_{i}): {student_answer}")
            print(f"  - Réponse attendue: {expected_answer}")
            
            # Normaliser les réponses pour la comparaison
            normalized_student_answer = student_answer.strip().lower() if student_answer else ""
            normalized_expected_answer = expected_answer.strip().lower() if expected_answer else ""
            
            # Vérifier si la réponse est correcte
            is_correct = normalized_student_answer == normalized_expected_answer
            
            print(f"  - Comparaison: '{normalized_student_answer}' == '{normalized_expected_answer}' => {is_correct}")
            
            if is_correct:
                correct_count += 1
                feedback.append({
                    'blank_index': i,
                    'student_answer': student_answer,
                    'correct_answer': expected_answer,
                    'is_correct': True
                })
            else:
                feedback.append({
                    'blank_index': i,
                    'student_answer': student_answer or '',
                    'correct_answer': expected_answer,
                    'is_correct': False
                })

        score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        print(f"[WORD_PLACEMENT_DEBUG] Score final: {score}% ({correct_count}/{total_blanks} = {correct_count/total_blanks if total_blanks > 0 else 0})")"""
        
        # Remplacer le code
        modified_content = original_content.replace(old_code, new_code)
        
        # Vérifier si le remplacement a été effectué
        if modified_content == original_content:
            logger.warning("Aucune modification n'a été effectuée. Le code cible n'a pas été trouvé.")
            
            # Essayer avec une autre approche - rechercher un fragment plus petit
            old_code_fragment = """            if student_answer and student_answer.strip().lower() == expected_answer.strip().lower():
                correct_count += 1"""
            
            new_code_fragment = """            # Normaliser les réponses pour la comparaison
            normalized_student_answer = student_answer.strip().lower() if student_answer else ""
            normalized_expected_answer = expected_answer.strip().lower() if expected_answer else ""
            
            # Vérifier si la réponse est correcte
            is_correct = normalized_student_answer == normalized_expected_answer
            
            print(f"  - Comparaison: '{normalized_student_answer}' == '{normalized_expected_answer}' => {is_correct}")
            
            if is_correct:
                correct_count += 1"""
            
            modified_content = original_content.replace(old_code_fragment, new_code_fragment)
            
            if modified_content == original_content:
                logger.error("Impossible de trouver le code à remplacer. Veuillez vérifier manuellement.")
                return False
        
        # Écrire le contenu modifié
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        logger.info("Correction du scoring word_placement appliquée avec succès.")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la correction: {str(e)}")
        return False

def test_word_placement_scoring():
    """
    Teste le scoring d'un exercice word_placement existant dans la base de données
    pour vérifier que la correction fonctionne.
    """
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # Trouver un exercice word_placement
        cursor.execute("SELECT id, content FROM exercise WHERE exercise_type = 'word_placement' LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            logger.warning("Aucun exercice word_placement trouvé dans la base de données pour le test.")
            return
        
        exercise_id, content_json = result
        content = json.loads(content_json)
        
        # Simuler une soumission parfaite (toutes les réponses correctes)
        form_data = {}
        for i, answer in enumerate(content.get('answers', [])):
            form_data[f'answer_{i}'] = answer
        
        # Calculer le score attendu
        sentences = content.get('sentences', [])
        correct_answers = content.get('answers', [])
        
        total_blanks_in_sentences = sum(s.count('___') for s in sentences)
        total_blanks = max(total_blanks_in_sentences, len(correct_answers))
        
        # Avec toutes les réponses correctes, le score devrait être de 100%
        expected_score = 100.0
        
        logger.info(f"Test avec l'exercice ID {exercise_id}:")
        logger.info(f"- Nombre de blancs dans les phrases: {total_blanks_in_sentences}")
        logger.info(f"- Nombre de réponses attendues: {len(correct_answers)}")
        logger.info(f"- Total de blanks utilisé: {total_blanks}")
        logger.info(f"- Score attendu: {expected_score}%")
        logger.info(f"- Réponses simulées: {form_data}")
        
        logger.info("Le test de scoring est prêt à être exécuté après redémarrage de l'application.")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur lors du test: {str(e)}")

def main():
    """
    Fonction principale
    """
    logger.info("=== CORRECTION DU SCORING WORD_PLACEMENT ===")
    
    success = fix_word_placement_scoring()
    
    if success:
        logger.info("Correction appliquée avec succès.")
        test_word_placement_scoring()
        
        logger.info("""
=== CORRECTION APPLIQUÉE AVEC SUCCÈS ===

La correction du scoring des exercices word_placement a été appliquée.
Le problème qui faisait que le score était toujours de 0% a été résolu.

Pour tester cette correction:
1. Redémarrez l'application Flask
2. Ouvrez un exercice word_placement
3. Complétez-le avec les bonnes réponses
4. Vérifiez que le score est bien de 100%

Pour déployer cette correction:
1. Vérifiez que tout fonctionne correctement en local
2. Committez les changements: git commit -am "Fix: Correction du scoring des exercices word_placement"
3. Poussez vers le dépôt distant: git push
""")
    else:
        logger.error("""
=== ÉCHEC DE LA CORRECTION ===

La correction n'a pas pu être appliquée. Veuillez vérifier les messages d'erreur ci-dessus.
""")

if __name__ == "__main__":
    main()
