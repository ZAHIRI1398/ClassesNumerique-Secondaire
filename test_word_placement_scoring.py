import os
import sys
import json
import sqlite3
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_word_placement_scoring():
    """
    Script de test pour vérifier le comportement du scoring des exercices word_placement
    avec différents scénarios de blancs et réponses.
    """
    try:
        # Connexion à la base de données
        db_path = 'instance/app.db'
        if not os.path.exists(db_path):
            logger.error(f"Base de données non trouvée: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices word_placement
        cursor.execute("SELECT id, title, content FROM exercise WHERE exercise_type = 'word_placement'")
        exercises = cursor.fetchall()
        
        if not exercises:
            logger.warning("Aucun exercice word_placement trouvé dans la base de données.")
            return False
        
        logger.info(f"Nombre d'exercices word_placement trouvés: {len(exercises)}")
        
        # Analyser chaque exercice
        for exercise_id, title, content_str in exercises:
            try:
                content = json.loads(content_str)
                logger.info(f"\n=== Exercice #{exercise_id}: {title} ===")
                
                # Vérifier la structure
                has_sentences = 'sentences' in content
                has_words = 'words' in content
                has_answers = 'answers' in content
                
                logger.info(f"Structure: sentences={has_sentences}, words={has_words}, answers={has_answers}")
                
                if not has_sentences or not has_answers:
                    logger.warning(f"Structure incomplète: sentences={has_sentences}, answers={has_answers}")
                    continue
                
                # Compter les blancs dans les phrases
                sentences = content['sentences']
                blanks_per_sentence = [s.count('___') for s in sentences]
                total_blanks_in_sentences = sum(blanks_per_sentence)
                
                # Compter les réponses
                answers = content['answers']
                total_answers = len(answers)
                
                logger.info(f"Blancs dans les phrases: {total_blanks_in_sentences}")
                logger.info(f"Nombre de réponses: {total_answers}")
                
                # Détails par phrase
                for i, sentence in enumerate(sentences):
                    logger.info(f"  Phrase {i+1}: '{sentence}' - {blanks_per_sentence[i]} blancs")
                
                # Détails des réponses
                for i, answer in enumerate(answers):
                    logger.info(f"  Réponse {i+1}: '{answer}'")
                
                # Vérifier la cohérence
                is_consistent = total_blanks_in_sentences == total_answers
                logger.info(f"Cohérence: {is_consistent}")
                
                # Simuler différentes logiques de scoring
                # Scénario 1: Toutes les réponses sont correctes
                
                # Logique 1: Utiliser uniquement le nombre de réponses
                logic1_total = total_answers
                logic1_score = 100.0  # Toutes les réponses sont correctes
                
                # Logique 2: Utiliser uniquement le nombre de blancs
                logic2_total = total_blanks_in_sentences
                logic2_score = (min(total_answers, total_blanks_in_sentences) / total_blanks_in_sentences) * 100 if total_blanks_in_sentences > 0 else 0
                
                # Logique 3: Utiliser le maximum entre blancs et réponses (logique actuelle)
                logic3_total = max(total_blanks_in_sentences, total_answers)
                logic3_score = (total_answers / logic3_total) * 100 if logic3_total > 0 else 0
                
                logger.info("\nSimulation de scoring (toutes réponses correctes):")
                logger.info(f"  Logique 1 (nombre de réponses): {logic1_score:.1f}% ({total_answers}/{logic1_total})")
                logger.info(f"  Logique 2 (nombre de blancs): {logic2_score:.1f}% ({min(total_answers, total_blanks_in_sentences)}/{logic2_total})")
                logger.info(f"  Logique 3 (max des deux): {logic3_score:.1f}% ({total_answers}/{logic3_total})")
                
                # Récupérer les tentatives pour cet exercice
                cursor.execute("""
                    SELECT id, student_id, score, answers, feedback, created_at 
                    FROM exercise_attempt 
                    WHERE exercise_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """, (exercise_id,))
                
                attempts = cursor.fetchall()
                
                if attempts:
                    logger.info("\nDernières tentatives:")
                    for attempt_id, student_id, score, answers_str, feedback_str, created_at in attempts:
                        try:
                            feedback = json.loads(feedback_str) if feedback_str else []
                            answers = json.loads(answers_str) if answers_str else {}
                            
                            # Compter les réponses correctes
                            correct_count = sum(1 for item in feedback if item.get('is_correct', False))
                            
                            logger.info(f"  Tentative #{attempt_id}: Étudiant #{student_id}, Score={score:.1f}%, Correctes={correct_count}/{len(feedback)}")
                            
                            # Recalculer le score avec les différentes logiques
                            recalc1 = (correct_count / logic1_total) * 100 if logic1_total > 0 else 0
                            recalc2 = (correct_count / logic2_total) * 100 if logic2_total > 0 else 0
                            recalc3 = (correct_count / logic3_total) * 100 if logic3_total > 0 else 0
                            
                            logger.info(f"    Score recalculé (Logique 1): {recalc1:.1f}%")
                            logger.info(f"    Score recalculé (Logique 2): {recalc2:.1f}%")
                            logger.info(f"    Score recalculé (Logique 3): {recalc3:.1f}%")
                            logger.info(f"    Score enregistré: {score:.1f}%")
                            
                            # Vérifier si le score enregistré correspond à l'une des logiques
                            matches_logic1 = abs(score - recalc1) < 0.1
                            matches_logic2 = abs(score - recalc2) < 0.1
                            matches_logic3 = abs(score - recalc3) < 0.1
                            
                            logger.info(f"    Correspond à Logique 1: {matches_logic1}")
                            logger.info(f"    Correspond à Logique 2: {matches_logic2}")
                            logger.info(f"    Correspond à Logique 3: {matches_logic3}")
                            
                        except Exception as e:
                            logger.error(f"Erreur lors de l'analyse de la tentative #{attempt_id}: {str(e)}")
                else:
                    logger.info("Aucune tentative trouvée pour cet exercice.")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de l'exercice #{exercise_id}: {str(e)}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors du test: {str(e)}")
        return False

def create_test_exercise():
    """
    Crée un exercice de test word_placement avec un nombre connu de blancs et de réponses
    pour vérifier le comportement du scoring.
    """
    try:
        # Connexion à la base de données
        db_path = 'instance/app.db'
        if not os.path.exists(db_path):
            logger.error(f"Base de données non trouvée: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si l'exercice de test existe déjà
        cursor.execute("SELECT id FROM exercise WHERE title = 'Test Word Placement Scoring'")
        existing = cursor.fetchone()
        
        if existing:
            logger.info(f"L'exercice de test existe déjà (ID: {existing[0]})")
            exercise_id = existing[0]
            
            # Mettre à jour l'exercice existant
            content = {
                'sentences': [
                    "1) Le chat ___ sur le tapis.",
                    "2) Les enfants ___ dans le parc.",
                    "3) Nous ___ au cinéma hier soir."
                ],
                'words': ["dort", "jouent", "sommes allés", "mangent", "écoutent"],
                'answers': ["dort", "jouent", "sommes allés"]
            }
            
            cursor.execute(
                "UPDATE exercise SET content = ? WHERE id = ?",
                (json.dumps(content), exercise_id)
            )
            conn.commit()
            logger.info(f"Exercice de test mis à jour (ID: {exercise_id})")
        else:
            # Créer un nouvel exercice de test
            content = {
                'sentences': [
                    "1) Le chat ___ sur le tapis.",
                    "2) Les enfants ___ dans le parc.",
                    "3) Nous ___ au cinéma hier soir."
                ],
                'words': ["dort", "jouent", "sommes allés", "mangent", "écoutent"],
                'answers': ["dort", "jouent", "sommes allés"]
            }
            
            # Récupérer l'ID du premier utilisateur admin
            cursor.execute("SELECT id FROM user WHERE is_admin = 1 LIMIT 1")
            admin_id = cursor.fetchone()
            
            if not admin_id:
                logger.error("Aucun utilisateur admin trouvé.")
                conn.close()
                return False
            
            admin_id = admin_id[0]
            
            # Insérer l'exercice
            cursor.execute(
                """
                INSERT INTO exercise (title, description, exercise_type, difficulty, content, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    "Test Word Placement Scoring",
                    "Exercice de test pour vérifier le scoring des exercices word_placement",
                    "word_placement",
                    "medium",
                    json.dumps(content),
                    admin_id
                )
            )
            conn.commit()
            
            # Récupérer l'ID de l'exercice créé
            cursor.execute("SELECT last_insert_rowid()")
            exercise_id = cursor.fetchone()[0]
            
            logger.info(f"Exercice de test créé (ID: {exercise_id})")
        
        conn.close()
        return exercise_id
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'exercice de test: {str(e)}")
        return False

def main():
    """
    Fonction principale
    """
    logger.info("=== TEST DU SCORING DES EXERCICES WORD_PLACEMENT ===")
    
    # Créer un exercice de test
    exercise_id = create_test_exercise()
    
    if exercise_id:
        logger.info(f"Exercice de test créé/mis à jour avec succès (ID: {exercise_id})")
    else:
        logger.warning("Impossible de créer l'exercice de test.")
    
    # Tester le scoring
    success = test_word_placement_scoring()
    
    if success:
        logger.info("""
=== TEST TERMINÉ AVEC SUCCÈS ===

Le test du scoring des exercices word_placement est terminé.
Consultez les résultats ci-dessus pour voir comment les différentes logiques de scoring
se comportent avec les exercices existants.

Pour tester l'exercice spécifique créé pour ce test:
1. Lancez l'application Flask
2. Connectez-vous en tant qu'administrateur
3. Accédez à l'exercice "Test Word Placement Scoring"
4. Testez le scoring avec différentes réponses

La logique de scoring actuelle utilise le maximum entre:
- Le nombre de blancs dans les phrases
- Le nombre de réponses attendues

Cette approche est la plus robuste car elle gère correctement les cas où:
- Il y a plus de blancs que de réponses
- Il y a plus de réponses que de blancs
""")
    else:
        logger.error("""
=== ÉCHEC DU TEST ===

Le test du scoring des exercices word_placement a échoué.
Vérifiez les messages d'erreur ci-dessus.
""")

if __name__ == "__main__":
    main()
