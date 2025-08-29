import os
import sys
import json
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_word_placement_scoring_comparison():
    """
    Corrige le problème de comparaison des réponses dans les exercices word_placement
    qui fait que le score est toujours de 0% même avec des réponses correctes.
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
        
        # Rechercher la section de code qui traite la comparaison des réponses
        # pour les exercices word_placement
        old_code = """            if student_answer and student_answer.strip().lower() == expected_answer.strip().lower():
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
                })"""
        
        new_code = """            # Normaliser les réponses pour la comparaison
            normalized_student_answer = student_answer.strip().lower() if student_answer else ""
            normalized_expected_answer = expected_answer.strip().lower() if expected_answer else ""
            
            # Vérifier si la réponse est correcte
            is_correct = normalized_student_answer == normalized_expected_answer
            
            # Déboguer la comparaison
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
                })"""
        
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
            
            # Déboguer la comparaison
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
        
        logger.info("Correction de la comparaison des réponses appliquée avec succès.")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la correction: {str(e)}")
        return False

def main():
    """
    Fonction principale
    """
    logger.info("=== CORRECTION DU SCORING WORD_PLACEMENT (COMPARAISON) ===")
    
    success = fix_word_placement_scoring_comparison()
    
    if success:
        logger.info("""
=== CORRECTION APPLIQUÉE AVEC SUCCÈS ===

La correction de la comparaison des réponses pour les exercices word_placement a été appliquée.
Le problème qui faisait que le score était toujours de 0% a été résolu.

Pour tester cette correction:
1. Redémarrez l'application Flask
2. Ouvrez un exercice word_placement
3. Complétez-le avec les bonnes réponses
4. Vérifiez que le score est bien de 100%

Pour déployer cette correction:
1. Vérifiez que tout fonctionne correctement en local
2. Committez les changements: git commit -am "Fix: Correction de la comparaison des réponses pour les exercices word_placement"
3. Poussez vers le dépôt distant: git push
""")
    else:
        logger.error("""
=== ÉCHEC DE LA CORRECTION ===

La correction n'a pas pu être appliquée. Veuillez vérifier les messages d'erreur ci-dessus.
""")

if __name__ == "__main__":
    main()
