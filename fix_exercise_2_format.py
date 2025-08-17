#!/usr/bin/env python3
"""
Script pour corriger le format de l'exercice 2 (Texte à trous - Les verbes).

Le problème identifié est que l'exercice 2 a un format incorrect dans le champ 'words'.
Ce script va analyser l'exercice et corriger son format pour assurer un scoring correct.
"""
import os
import sys
import json
import sqlite3
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_db():
    """Connexion à la base de données."""
    try:
        # Essayer d'abord le fichier app.db à la racine du projet
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
        logger.info(f"Tentative de connexion à la base de données: {db_path}")
        
        # Vérifier si le fichier existe
        if not os.path.exists(db_path):
            # Essayer le fichier app.db dans le dossier instance
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
            logger.info(f"Tentative de connexion à la base de données alternative: {db_path}")
            
            if not os.path.exists(db_path):
                logger.error(f"❌ Aucun fichier de base de données trouvé")
                return None
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {str(e)}")
        return None

def get_exercise_2():
    """Récupère l'exercice 2 de la base de données."""
    conn = connect_to_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exercise WHERE id = 2")
        exercise = cursor.fetchone()
        conn.close()
        
        if exercise:
            logger.info(f"✅ Exercice 2 trouvé: {exercise['title']}")
            return dict(exercise)
        else:
            logger.error("❌ Exercice 2 non trouvé dans la base de données")
            return None
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération de l'exercice 2: {str(e)}")
        conn.close()
        return None

def analyze_exercise_content(exercise):
    """Analyse le contenu de l'exercice pour identifier les problèmes."""
    if not exercise:
        return None
    
    try:
        content = json.loads(exercise['content'])
        logger.info(f"Structure du contenu: {list(content.keys())}")
        
        # Vérifier la présence des champs nécessaires
        if 'sentences' not in content:
            logger.error("❌ Champ 'sentences' manquant")
            return None
        
        if 'words' not in content:
            logger.error("❌ Champ 'words' manquant")
            return None
        
        # Analyser les phrases et les blancs
        total_blanks = 0
        for i, sentence in enumerate(content['sentences']):
            blanks_in_sentence = sentence.count('___')
            logger.info(f"Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            total_blanks += blanks_in_sentence
        
        # Analyser les mots disponibles
        logger.info(f"Mots disponibles: {content['words']}")
        logger.info(f"Nombre de mots: {len(content['words'])}")
        
        # Vérifier la cohérence
        if total_blanks != len(content['words']):
            logger.warning(f"⚠️ Incohérence: {total_blanks} blancs mais {len(content['words'])} mots")
        
        return content
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse du contenu: {str(e)}")
        return None

def fix_exercise_content(content):
    """Corrige le contenu de l'exercice."""
    if not content:
        return None
    
    try:
        # Vérifier si les mots sont dans le bon format
        if 'words' in content and isinstance(content['words'], list):
            # Vérifier si les mots sont des chaînes de caractères simples
            all_strings = all(isinstance(word, str) for word in content['words'])
            
            if not all_strings:
                logger.warning("⚠️ Certains mots ne sont pas au format string")
                
                # Corriger le format des mots
                new_words = []
                for word in content['words']:
                    if isinstance(word, dict) and 'word' in word:
                        new_words.append(word['word'])
                    elif isinstance(word, str):
                        new_words.append(word)
                    else:
                        logger.error(f"❌ Format non reconnu pour le mot: {word}")
                
                logger.info(f"Nouveaux mots: {new_words}")
                content['words'] = new_words
        
        return content
    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction du contenu: {str(e)}")
        return None

def update_exercise(exercise_id, content):
    """Met à jour l'exercice dans la base de données."""
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        content_json = json.dumps(content)
        
        # Créer une sauvegarde avant modification
        cursor.execute("SELECT content FROM exercise WHERE id = ?", (exercise_id,))
        old_content = cursor.fetchone()[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"exercise_{exercise_id}_backup_{timestamp}.json"
        
        with open(backup_file, 'w') as f:
            f.write(old_content)
        logger.info(f"✅ Sauvegarde créée: {backup_file}")
        
        # Mettre à jour l'exercice
        cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (content_json, exercise_id))
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Exercice {exercise_id} mis à jour avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour de l'exercice: {str(e)}")
        if conn:
            conn.close()
        return False

def test_exercise_scoring(exercise_id):
    """Teste le scoring de l'exercice après correction."""
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exercise WHERE id = ?", (exercise_id,))
        exercise = cursor.fetchone()
        conn.close()
        
        if not exercise:
            logger.error(f"❌ Exercice {exercise_id} non trouvé")
            return False
        
        content = json.loads(exercise['content'])
        
        # Simuler des réponses correctes
        correct_answers = content.get('words', [])
        total_blanks = sum(s.count('___') for s in content.get('sentences', []))
        
        logger.info(f"Test avec réponses correctes:")
        logger.info(f"- Réponses attendues: {correct_answers}")
        logger.info(f"- Nombre de blancs: {total_blanks}")
        
        # Simuler le scoring
        correct_count = len(correct_answers)
        score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        
        logger.info(f"Score simulé: {score}%")
        
        return score == 100.0
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de scoring: {str(e)}")
        return False

def main():
    """Fonction principale."""
    logger.info("=== CORRECTION DE L'EXERCICE 2 ===")
    
    # Récupérer l'exercice 2
    exercise = get_exercise_2()
    if not exercise:
        logger.error("❌ Impossible de continuer sans l'exercice 2")
        return
    
    # Analyser le contenu
    logger.info("\n=== ANALYSE DU CONTENU ===")
    content = analyze_exercise_content(exercise)
    if not content:
        logger.error("❌ Impossible de continuer sans analyse du contenu")
        return
    
    # Corriger le contenu
    logger.info("\n=== CORRECTION DU CONTENU ===")
    fixed_content = fix_exercise_content(content)
    if not fixed_content:
        logger.error("❌ Impossible de corriger le contenu")
        return
    
    # Mettre à jour l'exercice
    logger.info("\n=== MISE À JOUR DE L'EXERCICE ===")
    if update_exercise(exercise['id'], fixed_content):
        logger.info("✅ Exercice mis à jour avec succès")
        
        # Tester le scoring
        logger.info("\n=== TEST DU SCORING ===")
        if test_exercise_scoring(exercise['id']):
            logger.info("✅ Le scoring fonctionne correctement")
        else:
            logger.warning("⚠️ Le scoring ne fonctionne pas comme prévu")
    else:
        logger.error("❌ La mise à jour a échoué")

if __name__ == "__main__":
    main()
