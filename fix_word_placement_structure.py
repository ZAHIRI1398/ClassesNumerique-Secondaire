import os
import sys
import json
import sqlite3
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_word_placement_exercises():
    """
    Corrige la structure des exercices word_placement en ajoutant le champ 'answers'
    basé sur les mots disponibles et le nombre de blancs dans les phrases.
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
        
        # Analyser et corriger chaque exercice
        for exercise_id, title, content_str in exercises:
            try:
                content = json.loads(content_str)
                logger.info(f"\n=== Exercice #{exercise_id}: {title} ===")
                
                # Vérifier la structure
                has_sentences = 'sentences' in content
                has_words = 'words' in content
                has_answers = 'answers' in content
                
                logger.info(f"Structure actuelle: sentences={has_sentences}, words={has_words}, answers={has_answers}")
                
                if not has_sentences:
                    logger.warning(f"L'exercice #{exercise_id} n'a pas de phrases. Impossible de corriger.")
                    continue
                
                # Compter les blancs dans les phrases
                sentences = content['sentences']
                blanks_per_sentence = [s.count('___') for s in sentences]
                total_blanks_in_sentences = sum(blanks_per_sentence)
                
                logger.info(f"Nombre de blancs dans les phrases: {total_blanks_in_sentences}")
                
                # Si l'exercice n'a pas de champ 'answers', le créer
                if not has_answers:
                    # Si l'exercice a des mots, utiliser les premiers mots comme réponses
                    if has_words and 'words' in content and len(content['words']) > 0:
                        words = content['words']
                        
                        # Utiliser autant de mots que de blancs, ou tous les mots disponibles si moins
                        answers = words[:min(total_blanks_in_sentences, len(words))]
                        
                        # Si pas assez de mots, répéter le dernier mot
                        while len(answers) < total_blanks_in_sentences:
                            if len(words) > 0:
                                answers.append(words[-1])
                            else:
                                answers.append("mot_manquant")
                        
                        # Ajouter le champ 'answers' au contenu
                        content['answers'] = answers
                        
                        # Mettre à jour l'exercice dans la base de données
                        cursor.execute(
                            "UPDATE exercise SET content = ? WHERE id = ?",
                            (json.dumps(content), exercise_id)
                        )
                        conn.commit()
                        
                        logger.info(f"Exercice #{exercise_id} corrigé: champ 'answers' ajouté avec {len(answers)} réponses")
                        logger.info(f"Réponses ajoutées: {answers}")
                    else:
                        logger.warning(f"L'exercice #{exercise_id} n'a pas de mots disponibles. Impossible de créer des réponses.")
                else:
                    # Vérifier si le nombre de réponses correspond au nombre de blancs
                    answers = content['answers']
                    if len(answers) != total_blanks_in_sentences:
                        logger.warning(f"L'exercice #{exercise_id} a {len(answers)} réponses pour {total_blanks_in_sentences} blancs.")
                        
                        # Ajuster le nombre de réponses si nécessaire
                        if len(answers) < total_blanks_in_sentences:
                            # Ajouter des réponses manquantes
                            while len(answers) < total_blanks_in_sentences:
                                if len(answers) > 0:
                                    answers.append(answers[-1])
                                else:
                                    answers.append("réponse_manquante")
                            
                            content['answers'] = answers
                            
                            # Mettre à jour l'exercice dans la base de données
                            cursor.execute(
                                "UPDATE exercise SET content = ? WHERE id = ?",
                                (json.dumps(content), exercise_id)
                            )
                            conn.commit()
                            
                            logger.info(f"Exercice #{exercise_id} corrigé: réponses ajustées à {len(answers)}")
                        elif len(answers) > total_blanks_in_sentences:
                            # Réduire le nombre de réponses
                            answers = answers[:total_blanks_in_sentences]
                            content['answers'] = answers
                            
                            # Mettre à jour l'exercice dans la base de données
                            cursor.execute(
                                "UPDATE exercise SET content = ? WHERE id = ?",
                                (json.dumps(content), exercise_id)
                            )
                            conn.commit()
                            
                            logger.info(f"Exercice #{exercise_id} corrigé: réponses réduites à {len(answers)}")
                    else:
                        logger.info(f"L'exercice #{exercise_id} a déjà un nombre correct de réponses ({len(answers)}).")
                
            except Exception as e:
                logger.error(f"Erreur lors de la correction de l'exercice #{exercise_id}: {str(e)}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la correction des exercices: {str(e)}")
        return False

def main():
    """
    Fonction principale
    """
    logger.info("=== CORRECTION DE LA STRUCTURE DES EXERCICES WORD_PLACEMENT ===")
    
    # Créer une sauvegarde de la base de données
    db_path = 'instance/app.db'
    backup_path = f'instance/app.db.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    try:
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            logger.info(f"Sauvegarde de la base de données créée: {backup_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la création de la sauvegarde: {str(e)}")
        return
    
    # Corriger les exercices
    success = fix_word_placement_exercises()
    
    if success:
        logger.info("""
=== CORRECTION TERMINÉE AVEC SUCCÈS ===

La structure des exercices word_placement a été corrigée.
Pour chaque exercice sans champ 'answers':
- Un champ 'answers' a été ajouté avec des réponses basées sur les mots disponibles
- Le nombre de réponses a été ajusté pour correspondre au nombre de blancs dans les phrases

Pour vérifier les résultats:
1. Lancez l'application Flask
2. Connectez-vous en tant qu'administrateur
3. Accédez aux exercices word_placement et vérifiez qu'ils fonctionnent correctement

Si vous rencontrez des problèmes, vous pouvez restaurer la base de données à partir de la sauvegarde.
""")
    else:
        logger.error("""
=== ÉCHEC DE LA CORRECTION ===

La correction de la structure des exercices word_placement a échoué.
Vérifiez les messages d'erreur ci-dessus.
""")

if __name__ == "__main__":
    main()
