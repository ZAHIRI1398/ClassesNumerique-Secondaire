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
        
        # Rechercher l'exercice "Les coordonnées"
        cursor.execute("SELECT id, title, exercise_type, content FROM exercise WHERE title LIKE '%coordonnées%'")
        result = cursor.fetchone()
        
        if not result:
            logger.warning("Aucun exercice avec 'coordonnées' dans le titre n'a été trouvé.")
            # Essayons de trouver des exercices similaires
            cursor.execute("SELECT id, title, exercise_type FROM exercise WHERE title LIKE '%coord%'")
            similar_exercises = cursor.fetchall()
            if similar_exercises:
                logger.info("Exercices similaires trouvés:")
                for ex in similar_exercises:
                    logger.info(f"ID: {ex[0]}, Titre: {ex[1]}, Type: {ex[2]}")
            return
        
        exercise_id, title, exercise_type, content_str = result
        content = json.loads(content_str)
        
        logger.info(f"=== ANALYSE DE L'EXERCICE 'LES COORDONNÉES' ===")
        logger.info(f"ID: {exercise_id}")
        logger.info(f"Titre: {title}")
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
        total_blanks = max(text_blanks, sentences_blanks)
        logger.info(f"Total blanks (max entre text et sentences): {total_blanks}")
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
        
        # Analyser le code de scoring dans app.py
        logger.info("\n=== ANALYSE DU CODE DE SCORING ===")
        
        # Vérifier si app.py existe
        if not os.path.exists('app.py'):
            logger.warning("Le fichier app.py n'existe pas.")
            return
        
        # Extraire la partie du code qui gère le scoring pour fill_in_blanks
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Chercher la section de code qui traite fill_in_blanks
        fill_in_blanks_section_start = app_content.find("elif exercise.exercise_type == 'fill_in_blanks':")
        if fill_in_blanks_section_start == -1:
            logger.warning("Section de code pour fill_in_blanks non trouvée.")
            return
        
        # Extraire une partie du code pour analyse
        fill_in_blanks_code = app_content[fill_in_blanks_section_start:fill_in_blanks_section_start+1000]
        logger.info("Code de scoring pour fill_in_blanks (extrait):")
        for i, line in enumerate(fill_in_blanks_code.split('\n')[:30]):
            logger.info(f"{i+1}: {line}")
        
        # Conclusion et recommandations
        logger.info("\n=== CONCLUSION ET RECOMMANDATIONS ===")
        
        if exercise_type != 'fill_in_blanks':
            logger.warning(f"L'exercice 'Les coordonnées' est de type '{exercise_type}', pas 'fill_in_blanks'!")
            logger.warning("La correction que nous avons déployée ne s'applique donc pas à cet exercice.")
            logger.info("Recommandation: Vérifier la logique de scoring pour ce type d'exercice spécifique.")
        elif total_blanks != answers_count:
            logger.warning("Le problème semble être une incohérence entre le nombre de blancs et le nombre de réponses.")
            logger.info("Recommandation: Vérifier la structure du contenu de l'exercice et ajuster soit les blancs, soit les réponses.")
        else:
            logger.info("La structure de l'exercice semble correcte.")
            logger.info("Recommandation: Vérifier si la correction a bien été déployée et si elle s'applique correctement à cet exercice.")
    
    except Exception as e:
        logger.error(f"Erreur lors du debug: {str(e)}")

if __name__ == "__main__":
    debug_coordonnees_exercise()
