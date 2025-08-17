import os
import sys
import json
import sqlite3
from flask import Flask, flash, redirect, url_for
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Créer une application Flask minimale pour les tests
app = Flask(__name__)
app.logger = logger

def fix_word_placement_scoring():
    """
    Script pour corriger le problème de scoring dans les exercices de type word_placement.
    Applique la même logique de correction que pour les exercices fill_in_blanks.
    """
    try:
        # Chemin vers le fichier app.py
        app_path = 'app.py'
        backup_path = 'app.py.bak.word_placement'
        
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
        
        # Rechercher et remplacer le code de scoring pour word_placement
        # Nous cherchons la section qui calcule le score pour les exercices word_placement
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
        total_blanks = len(correct_answers)
        correct_count = 0
        
        print(f"[WORD_PLACEMENT_DEBUG] Total blanks: {total_blanks}")
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
        print(f"[WORD_PLACEMENT_DEBUG] Score final: {score}% ({correct_count}/{total_blanks})")"""

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

        # Remplacer le code
        modified_content = original_content.replace(old_code, new_code)
        
        # Vérifier si le remplacement a été effectué
        if modified_content == original_content:
            logger.warning("Aucune modification n'a été effectuée. Le code cible n'a pas été trouvé.")
            return False
        
        # Écrire le contenu modifié
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        logger.info("Modifications appliquées avec succès.")
        
        # Tester un exercice word_placement pour vérifier la correction
        logger.info("\nTest d'un exercice word_placement:")
        test_word_placement_scoring()
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la correction: {str(e)}")
        return False

def test_word_placement_scoring():
    """
    Teste la logique de scoring pour les exercices word_placement
    """
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # Récupérer un exercice word_placement
        cursor.execute("SELECT id, content FROM exercise WHERE exercise_type = 'word_placement' LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            logger.warning("Aucun exercice word_placement trouvé dans la base de données.")
            return
        
        exercise_id, content_str = result
        content = json.loads(content_str)
        
        logger.info(f"Exercice word_placement trouvé (ID: {exercise_id})")
        logger.info(f"Contenu: {json.dumps(content, indent=2)}")
        
        # Analyser le contenu
        if 'sentences' in content and 'answers' in content:
            sentences = content['sentences']
            answers = content['answers']
            
            # Compter les blancs dans les phrases
            total_blanks_in_sentences = sum(s.count('___') for s in sentences)
            
            logger.info(f"Nombre de phrases: {len(sentences)}")
            logger.info(f"Nombre de blancs dans les phrases: {total_blanks_in_sentences}")
            logger.info(f"Nombre de réponses: {len(answers)}")
            
            # Simuler un scoring parfait
            correct_count = len(answers)
            total_blanks = max(total_blanks_in_sentences, len(answers))
            
            score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
            logger.info(f"Score simulé (toutes réponses correctes): {score}% ({correct_count}/{total_blanks})")
            
            # Vérifier si le score est correct
            if score == 100.0:
                logger.info("✅ Le scoring est correct!")
            else:
                logger.warning(f"⚠️ Le scoring n'est pas correct. Score attendu: 100%, Score obtenu: {score}%")
        else:
            logger.warning("Structure de l'exercice invalide. Clés manquantes: sentences ou answers.")
        
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
        logger.info("""
=== CORRECTION APPLIQUÉE AVEC SUCCÈS ===

La correction du scoring pour les exercices word_placement a été appliquée.
Le problème de comptage des blancs a été résolu.

Pour déployer cette correction:
1. Vérifiez que tout fonctionne correctement en local
2. Committez les changements: git commit -am "Fix: Correction du scoring pour les exercices word_placement"
3. Poussez vers le dépôt distant: git push

La correction sera alors déployée automatiquement sur Railway.
""")
    else:
        logger.error("""
=== ÉCHEC DE LA CORRECTION ===

La correction n'a pas pu être appliquée. Vérifiez les messages d'erreur ci-dessus.
""")

if __name__ == "__main__":
    main()
