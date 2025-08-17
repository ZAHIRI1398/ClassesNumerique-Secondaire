import os
import sys
import json
import sqlite3
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_coordonnees_exercise():
    """
    Script pour analyser spécifiquement l'exercice "Les coordonnées" et comprendre
    pourquoi la correction du scoring ne s'applique pas correctement.
    """
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # Rechercher l'exercice avec des termes plus généraux
        cursor.execute("SELECT id, title, exercise_type, content FROM exercise WHERE title LIKE '%coord%' OR title LIKE '%Coord%'")
        results = cursor.fetchall()
        
        if not results:
            logger.warning("Aucun exercice avec 'coord' dans le titre n'a été trouvé.")
            return
        
        logger.info(f"Nombre d'exercices trouvés: {len(results)}")
        
        # Analyser chaque exercice trouvé
        for result in results:
            exercise_id, title, exercise_type, content_str = result
            content = json.loads(content_str)
            
            logger.info(f"\n\n=== ANALYSE DE L'EXERCICE '{title}' ===")
            logger.info(f"ID: {exercise_id}")
            logger.info(f"Type: {exercise_type}")
            logger.info(f"Contenu: {json.dumps(content, indent=2)}")
            
            # Analyser la structure du contenu
            logger.info("\n=== STRUCTURE DU CONTENU ===")
            for key in content:
                logger.info(f"Clé: {key}")
                if isinstance(content[key], list):
                    logger.info(f"  - Type: liste de {len(content[key])} éléments")
                    if len(content[key]) > 0:
                        logger.info(f"  - Premier élément: {content[key][0]}")
                else:
                    logger.info(f"  - Type: {type(content[key]).__name__}")
                    logger.info(f"  - Valeur: {content[key]}")
            
            # Analyser spécifiquement les blancs et les réponses
            logger.info("\n=== ANALYSE DES BLANCS ET RÉPONSES ===")
            
            # Compter les blancs dans le texte
            text_blanks = 0
            if 'text' in content:
                text_blanks = content['text'].count('___')
                logger.info(f"Blancs dans 'text': {text_blanks}")
                logger.info(f"Texte: {content['text']}")
            
            # Compter les blancs dans les phrases
            sentences_blanks = 0
            if 'sentences' in content:
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    logger.info(f"Phrase {i+1}: {sentence}")
                    logger.info(f"  - Blancs: {blanks_in_sentence}")
                    sentences_blanks += blanks_in_sentence
                logger.info(f"Total blancs dans 'sentences': {sentences_blanks}")
            
            # Analyser les réponses
            answers_count = 0
            if 'answers' in content:
                answers_count = len(content['answers'])
                logger.info(f"Nombre de réponses dans 'answers': {answers_count}")
                for i, answer in enumerate(content['answers']):
                    logger.info(f"Réponse {i+1}: {answer}")
            
            # Analyser les mots disponibles
            if 'available_words' in content:
                logger.info(f"Mots disponibles: {content['available_words']}")
            elif 'words' in content:
                logger.info(f"Mots disponibles (words): {content['words']}")
            
            # Vérifier la cohérence
            logger.info("\n=== VÉRIFICATION DE COHÉRENCE ===")
            
            # Déterminer le nombre total de blancs selon la logique corrigée
            if 'sentences' in content:
                total_blanks = sentences_blanks
            elif 'text' in content:
                total_blanks = text_blanks
            else:
                total_blanks = 0
            
            logger.info(f"Total blanks (priorité sentences puis text): {total_blanks}")
            logger.info(f"Nombre de réponses: {answers_count}")
            
            if total_blanks != answers_count and answers_count > 0:
                logger.warning(f"⚠️ INCOHÉRENCE: Le nombre de blancs ({total_blanks}) ne correspond pas au nombre de réponses ({answers_count})!")
            else:
                logger.info("✅ Cohérence OK: Le nombre de blanks correspond au nombre de réponses.")
            
            # Simuler le scoring
            logger.info("\n=== SIMULATION DE SCORING ===")
            
            # Simuler un scoring parfait (toutes les réponses correctes)
            if answers_count > 0:
                score = (answers_count / total_blanks) * 100 if total_blanks > 0 else 0
                logger.info(f"Score simulé (toutes réponses correctes): {score}% ({answers_count}/{total_blanks})")
                
                if score != 100.0:
                    logger.warning(f"⚠️ PROBLÈME DE SCORING: Le score devrait être 100% mais est calculé à {score}%")
                    
                    # Analyser pourquoi le score n'est pas 100%
                    if total_blanks > answers_count:
                        logger.warning(f"  - Il y a plus de blancs ({total_blanks}) que de réponses ({answers_count})")
                        logger.warning(f"  - Certains blancs n'ont pas de réponse associée")
                    elif total_blanks < answers_count:
                        logger.warning(f"  - Il y a moins de blancs ({total_blanks}) que de réponses ({answers_count})")
                        logger.warning(f"  - Certaines réponses ne correspondent à aucun blanc")
            
            # Vérifier si l'exercice a des tentatives
            logger.info("\n=== TENTATIVES DE L'EXERCICE ===")
            cursor.execute("""
                SELECT id, user_id, score, created_at 
                FROM exercise_attempt 
                WHERE exercise_id = ? 
                ORDER BY created_at DESC 
                LIMIT 5
            """, (exercise_id,))
            attempts = cursor.fetchall()
            
            if attempts:
                logger.info(f"Dernières tentatives:")
                for attempt in attempts:
                    attempt_id, user_id, score, created_at = attempt
                    logger.info(f"ID: {attempt_id}, Utilisateur: {user_id}, Score: {score}%, Date: {created_at}")
                    
                    # Récupérer les détails de la tentative
                    cursor.execute("SELECT data FROM exercise_attempt WHERE id = ?", (attempt_id,))
                    attempt_data = cursor.fetchone()
                    if attempt_data and attempt_data[0]:
                        try:
                            data = json.loads(attempt_data[0])
                            logger.info(f"  - Données: {json.dumps(data, indent=2)}")
                        except:
                            logger.info(f"  - Données: {attempt_data[0]}")
            else:
                logger.info("Aucune tentative trouvée pour cet exercice.")
        
        conn.close()
        
        # Conclusion et recommandations
        logger.info("\n=== CONCLUSION GÉNÉRALE ===")
        logger.info("Vérifiez les résultats ci-dessus pour identifier l'exercice problématique et comprendre pourquoi le scoring ne fonctionne pas correctement.")
    
    except Exception as e:
        logger.error(f"Erreur lors du debug: {str(e)}")

if __name__ == "__main__":
    debug_coordonnees_exercise()
