#!/usr/bin/env python3
"""
Script pour analyser spécifiquement l'exercice 2 et comprendre
pourquoi la correction du scoring ne s'applique pas correctement.
"""
import os
import sys
import json
import sqlite3
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_exercise_2():
    """
    Script pour analyser spécifiquement l'exercice 2 et comprendre
    sa structure et son scoring.
    """
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # Récupérer l'exercice 2
        cursor.execute("SELECT id, title, exercise_type, content FROM exercise WHERE id = 2")
        result = cursor.fetchone()
        
        if not result:
            logger.warning("L'exercice 2 n'a pas été trouvé.")
            return
        
        exercise_id, title, exercise_type, content_str = result
        content = json.loads(content_str)
        
        logger.info(f"=== ANALYSE DE L'EXERCICE 2 ===")
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
        
        # Analyser spécifiquement les blancs et les réponses selon le type d'exercice
        logger.info(f"\n=== ANALYSE DES BLANCS ET RÉPONSES POUR TYPE: {exercise_type} ===")
        
        if exercise_type == 'fill_in_blanks':
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
                answers_count = len(content['available_words'])
            elif 'words' in content:
                logger.info(f"Mots disponibles (words): {content['words']}")
                answers_count = len(content['words'])
            
            # Vérifier la cohérence
            logger.info("\n=== VÉRIFICATION DE COHÉRENCE ===")
            
            # Utiliser la logique corrigée pour compter les blancs
            if 'sentences' in content:
                total_blanks = sentences_blanks
            elif 'text' in content:
                total_blanks = text_blanks
            else:
                total_blanks = 0
                
            logger.info(f"Total blanks (logique corrigée): {total_blanks}")
            logger.info(f"Nombre de réponses: {answers_count}")
            
            if total_blanks != answers_count and answers_count > 0:
                logger.warning(f"⚠️ INCOHÉRENCE: Le nombre de blancs ({total_blanks}) ne correspond pas au nombre de réponses ({answers_count})!")
            else:
                logger.info("✅ Cohérence OK: Le nombre de blanks correspond au nombre de réponses.")
            
            # Simuler le scoring
            logger.info("\n=== SIMULATION DE SCORING ===")
            
            # Simuler un scoring parfait (toutes les réponses correctes)
            if answers_count > 0 and total_blanks > 0:
                score = (answers_count / total_blanks) * 100
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
        
        elif exercise_type == 'word_placement':
            # Analyser les phrases
            sentences_blanks = 0
            if 'sentences' in content:
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    logger.info(f"Phrase {i+1}: {sentence}")
                    logger.info(f"  - Blancs: {blanks_in_sentence}")
                    sentences_blanks += blanks_in_sentence
                logger.info(f"Total blancs dans 'sentences': {sentences_blanks}")
            
            # Analyser les mots
            words_count = 0
            if 'words' in content:
                words_count = len(content['words'])
                logger.info(f"Nombre de mots: {words_count}")
                logger.info(f"Mots: {content['words']}")
            
            # Vérifier la cohérence
            logger.info("\n=== VÉRIFICATION DE COHÉRENCE ===")
            logger.info(f"Total blancs: {sentences_blanks}")
            logger.info(f"Nombre de mots: {words_count}")
            
            if sentences_blanks != words_count and words_count > 0:
                logger.warning(f"⚠️ INCOHÉRENCE: Le nombre de blancs ({sentences_blanks}) ne correspond pas au nombre de mots ({words_count})!")
            else:
                logger.info("✅ Cohérence OK: Le nombre de blanks correspond au nombre de mots.")
        
        else:
            logger.info(f"Type d'exercice '{exercise_type}' non pris en charge par ce script de diagnostic.")
        
        # Vérifier si l'exercice a des tentatives
        logger.info("\n=== TENTATIVES DE L'EXERCICE ===")
        cursor.execute("""
            SELECT id, student_id, score, created_at 
            FROM exercise_attempt 
            WHERE exercise_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (exercise_id,))
        attempts = cursor.fetchall()
        
        if attempts:
            logger.info(f"Dernières tentatives:")
            for attempt in attempts:
                attempt_id, student_id, score, created_at = attempt
                logger.info(f"ID: {attempt_id}, Étudiant: {student_id}, Score: {score}%, Date: {created_at}")
                
                # Récupérer les détails de la tentative
                try:
                    # Vérifier les colonnes disponibles dans la table exercise_attempt
                    cursor.execute("PRAGMA table_info(exercise_attempt)")
                    columns = [column[1] for column in cursor.fetchall()]
                    logger.info(f"  - Colonnes disponibles: {columns}")
                    
                    # Récupérer les données de la tentative selon les colonnes disponibles
                    if 'data' in columns:
                        cursor.execute("SELECT data FROM exercise_attempt WHERE id = ?", (attempt_id,))
                        attempt_data = cursor.fetchone()
                        if attempt_data and attempt_data[0]:
                            try:
                                data = json.loads(attempt_data[0])
                                logger.info(f"  - Données: {json.dumps(data, indent=2)}")
                            except:
                                logger.info(f"  - Données: {attempt_data[0]}")
                    elif 'answers' in columns:
                        cursor.execute("SELECT answers FROM exercise_attempt WHERE id = ?", (attempt_id,))
                        attempt_data = cursor.fetchone()
                        if attempt_data and attempt_data[0]:
                            try:
                                data = json.loads(attempt_data[0])
                                logger.info(f"  - Réponses: {json.dumps(data, indent=2)}")
                            except:
                                logger.info(f"  - Réponses: {attempt_data[0]}")
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des détails de la tentative: {str(e)}")
                    pass
        else:
            logger.info("Aucune tentative trouvée pour cet exercice.")
        
        conn.close()
        
        # Conclusion et recommandations
        logger.info("\n=== CONCLUSION ET RECOMMANDATIONS ===")
        
        if exercise_type not in ['fill_in_blanks', 'word_placement']:
            logger.warning(f"L'exercice 2 est de type '{exercise_type}', pas 'fill_in_blanks' ou 'word_placement'!")
            logger.warning("La correction que nous avons déployée ne s'applique donc pas à cet exercice.")
            logger.info("Recommandation: Vérifier la logique de scoring pour ce type d'exercice spécifique.")
        elif exercise_type == 'fill_in_blanks' and total_blanks != answers_count:
            logger.warning("Le problème semble être une incohérence entre le nombre de blancs et le nombre de réponses.")
            logger.info("Recommandation: Vérifier la structure du contenu de l'exercice et ajuster soit les blancs, soit les réponses.")
        elif exercise_type == 'word_placement' and sentences_blanks != words_count:
            logger.warning("Le problème semble être une incohérence entre le nombre de blancs et le nombre de mots.")
            logger.info("Recommandation: Vérifier la structure du contenu de l'exercice et ajuster soit les blancs, soit les mots.")
        else:
            logger.info("La structure de l'exercice semble correcte.")
            logger.info("Recommandation: Vérifier si la correction a bien été déployée et si elle s'applique correctement à cet exercice.")
    
    except Exception as e:
        logger.error(f"Erreur lors du debug: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    debug_exercise_2()
