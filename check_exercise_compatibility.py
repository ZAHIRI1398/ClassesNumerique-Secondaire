#!/usr/bin/env python3
"""
Script pour vérifier la compatibilité de la modification du scoring insensible à l'ordre
avec les autres types d'exercices.
"""
import os
import sys
import json
import logging
import sqlite3
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_db():
    """Établit une connexion à la base de données."""
    try:
        conn = sqlite3.connect('app.db')
        conn.row_factory = sqlite3.Row
        logger.info("✅ Connexion à la base de données établie")
        return conn
    except sqlite3.Error as e:
        logger.error(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def get_exercise_types(conn):
    """
    Récupère tous les types d'exercices présents dans la base de données.
    
    Args:
        conn: Connexion à la base de données
        
    Returns:
        dict: Dictionnaire avec les types d'exercices et leur nombre
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT exercise_type, COUNT(*) as count FROM exercises GROUP BY exercise_type")
        types = cursor.fetchall()
        
        exercise_types = {}
        for t in types:
            exercise_types[t['exercise_type']] = t['count']
        
        logger.info(f"✅ Types d'exercices trouvés: {json.dumps(exercise_types, indent=2)}")
        return exercise_types
    
    except sqlite3.Error as e:
        logger.error(f"❌ Erreur lors de la récupération des types d'exercices: {e}")
        return {}

def check_app_py_for_exercise_types():
    """
    Analyse le fichier app.py pour vérifier comment chaque type d'exercice est traité.
    
    Returns:
        dict: Dictionnaire avec les types d'exercices et leur méthode de scoring
    """
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()
        
        # Rechercher les sections de traitement des exercices
        exercise_types = [
            'fill_in_blanks',
            'word_placement',
            'drag_and_drop',
            'pairs',
            'underline_words',
            'dictation',
            'image_labeling',
            'flashcards',
            'qcm_multichoix'
        ]
        
        exercise_scoring = {}
        
        for ex_type in exercise_types:
            # Rechercher le pattern pour ce type d'exercice
            pattern = f"elif exercise.exercise_type == '{ex_type}':"
            if pattern in app_content:
                # Trouver la section qui traite ce type d'exercice
                start_idx = app_content.find(pattern)
                section = app_content[start_idx:start_idx + 1000]  # Prendre une section suffisamment grande
                
                # Déterminer si ce type d'exercice utilise une logique similaire à fill_in_blanks
                uses_similar_logic = "correct_blanks" in section or "total_blanks" in section
                
                exercise_scoring[ex_type] = {
                    'found': True,
                    'uses_similar_logic': uses_similar_logic
                }
            else:
                exercise_scoring[ex_type] = {
                    'found': False,
                    'uses_similar_logic': False
                }
        
        logger.info(f"✅ Analyse du fichier app.py terminée")
        return exercise_scoring
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse de app.py: {str(e)}")
        return {}

def analyze_compatibility():
    """
    Analyse la compatibilité de la modification avec les autres types d'exercices.
    
    Returns:
        dict: Résultats de l'analyse
    """
    # Vérifier les types d'exercices dans app.py
    exercise_scoring = check_app_py_for_exercise_types()
    
    # Connexion à la base de données
    conn = connect_to_db()
    if not conn:
        logger.error("❌ Impossible de continuer sans connexion à la base de données")
        return {}
    
    # Récupérer les types d'exercices dans la base de données
    db_exercise_types = get_exercise_types(conn)
    conn.close()
    
    # Combiner les résultats
    compatibility_results = {}
    
    for ex_type, count in db_exercise_types.items():
        if ex_type in exercise_scoring:
            scoring_info = exercise_scoring[ex_type]
            
            # Déterminer la compatibilité
            if ex_type == 'fill_in_blanks':
                compatibility = 'Modifié'
                impact = 'Positif - Scoring insensible à l\'ordre'
            elif ex_type == 'word_placement' and scoring_info['uses_similar_logic']:
                compatibility = 'Potentiellement affecté'
                impact = 'Neutre - Logique similaire mais pas modifiée'
            elif scoring_info['uses_similar_logic']:
                compatibility = 'À surveiller'
                impact = 'Incertain - Utilise une logique similaire'
            else:
                compatibility = 'Compatible'
                impact = 'Aucun - Logique différente'
        else:
            compatibility = 'Inconnu'
            impact = 'Incertain - Type non analysé dans app.py'
        
        compatibility_results[ex_type] = {
            'count': count,
            'compatibility': compatibility,
            'impact': impact
        }
    
    return compatibility_results

def main():
    """Fonction principale."""
    logger.info("=== VÉRIFICATION DE LA COMPATIBILITÉ AVEC LES AUTRES TYPES D'EXERCICES ===")
    
    # Analyser la compatibilité
    compatibility_results = analyze_compatibility()
    
    # Afficher les résultats
    logger.info("\n=== RÉSULTATS DE L'ANALYSE DE COMPATIBILITÉ ===")
    
    for ex_type, info in compatibility_results.items():
        logger.info(f"\n--- Type: {ex_type} ({info['count']} exercice(s)) ---")
        logger.info(f"Compatibilité: {info['compatibility']}")
        logger.info(f"Impact: {info['impact']}")
    
    # Résumé
    affected_types = [ex_type for ex_type, info in compatibility_results.items() 
                     if info['compatibility'] in ['Modifié', 'Potentiellement affecté', 'À surveiller']]
    
    logger.info("\n=== RÉSUMÉ ===")
    if affected_types:
        logger.info(f"Types d'exercices à surveiller: {', '.join(affected_types)}")
        logger.info("Recommandation: Tester ces types d'exercices après le déploiement")
    else:
        logger.info("✅ Aucun autre type d'exercice ne devrait être affecté par la modification")
    
    # Créer un rapport
    report = {
        'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'results': compatibility_results,
        'affected_types': affected_types
    }
    
    with open("compatibility_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info("✅ Rapport de compatibilité créé: compatibility_report.json")

if __name__ == "__main__":
    main()
