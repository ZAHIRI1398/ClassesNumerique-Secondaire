#!/usr/bin/env python3
"""
Script pour corriger le problème de double comptage des blancs dans les exercices fill_in_blanks
"""

import os
import re
import sys
import json

def fix_fill_in_blanks_double_counting():
    """
    Corrige la logique de comptage des blancs dans les exercices fill_in_blanks
    pour éviter le double comptage entre 'text' et 'sentences'.
    """
    # Chemin vers app.py
    app_path = 'app.py'
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: Le fichier {app_path} n'existe pas.")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Faire une sauvegarde du fichier original
    backup_path = f"{app_path}.bak.double_counting"
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Sauvegarde créée: {backup_path}")
    
    # Rechercher la section de comptage des blancs
    blanks_counting_section = re.search(
        r"# Compter le nombre réel de blancs dans le contenu.*?app\.logger\.info\(f\"\[FILL_IN_BLANKS_DEBUG\] Total blanks found in content: \{total_blanks_in_content\}\"\)",
        content,
        re.DOTALL
    )
    
    if not blanks_counting_section:
        print("La section de comptage des blancs n'a pas été trouvée.")
        return False
    
    # Extraire la section à remplacer
    original_section = blanks_counting_section.group(0)
    
    # Créer la nouvelle section qui évite le double comptage
    new_section = """# Compter le nombre réel de blancs dans le contenu
            total_blanks_in_content = 0
            
            # Analyser le format de l'exercice et compter les blancs réels
            # CORRECTION: Éviter le double comptage entre 'text' et 'sentences'
            # Priorité à 'sentences' s'il existe, sinon utiliser 'text'
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
                # Log détaillé pour chaque phrase et ses blancs
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' détecté: {text_blanks} blancs dans text")
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Total blancs trouvés dans le contenu: {total_blanks_in_content}")"""
    
    # Remplacer la section dans le contenu
    modified_content = content.replace(original_section, new_section)
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Correction du double comptage des blancs appliquée avec succès!")
    return True

def test_fix():
    """
    Crée un script de test pour vérifier que la correction fonctionne
    """
    test_script_path = 'test_fill_in_blanks_fix.py'
    
    test_script_content = '''#!/usr/bin/env python3
"""
Script de test pour vérifier la correction du double comptage des blancs
"""

import sys
import json
sys.path.append('.')

from app import app, db, Exercise

def simulate_scoring(exercise_id):
    """Simule le scoring d'un exercice fill_in_blanks"""
    from app import json
    
    with app.app_context():
        exercise = Exercise.query.get(exercise_id)
        if not exercise or exercise.exercise_type != 'fill_in_blanks':
            print(f"Exercice {exercise_id} non trouvé ou n'est pas de type fill_in_blanks")
            return
        
        print(f"Simulation de scoring pour: {exercise.title} (ID: {exercise.id})")
        
        # Charger le contenu
        content = json.loads(exercise.content)
        
        # Compter le nombre réel de blancs dans le contenu
        total_blanks_in_content = 0
        
        # Analyser le format de l'exercice et compter les blancs réels
        # Priorité à 'sentences' s'il existe, sinon utiliser 'text'
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            print(f"Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
            for i, sentence in enumerate(content['sentences']):
                blanks_in_sentence = sentence.count('___')
                print(f"  Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"Format 'text' détecté: {text_blanks} blancs dans text")
            print(f"  Texte: {content['text']}")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        print(f"Total blancs trouvés: {total_blanks_in_content}")
        print(f"Réponses correctes: {correct_answers} (total: {len(correct_answers)})")
        
        # Vérifier la cohérence
        if total_blanks_in_content != len(correct_answers):
            print(f"[PROBLEME] INCOHÉRENCE: {total_blanks_in_content} blancs vs {len(correct_answers)} réponses")
            return False
        else:
            print(f"[OK] Cohérent: {total_blanks_in_content} blancs = {len(correct_answers)} réponses")
            return True
        
def test_all_exercises():
    """Teste tous les exercices fill_in_blanks"""
    with app.app_context():
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        
        if not exercises:
            print("Aucun exercice fill_in_blanks trouvé")
            return
        
        print(f"Trouvé {len(exercises)} exercices fill_in_blanks")
        
        all_ok = True
        for exercise in exercises:
            print(f"\\n{'='*50}")
            result = simulate_scoring(exercise.id)
            all_ok = all_ok and result
        
        if all_ok:
            print("\\n[SUCCÈS] Tous les exercices sont cohérents!")
        else:
            print("\\n[ÉCHEC] Certains exercices présentent des incohérences.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Tester un exercice spécifique
        exercise_id = int(sys.argv[1])
        simulate_scoring(exercise_id)
    else:
        # Tester tous les exercices
        test_all_exercises()
'''
    
    with open(test_script_path, 'w', encoding='utf-8') as file:
        file.write(test_script_content)
    
    print(f"Script de test créé: {test_script_path}")
    return True

if __name__ == '__main__':
    print("Correction du problème de double comptage des blancs dans les exercices fill_in_blanks...")
    fix_fill_in_blanks_double_counting()
    test_fix()
    print("Terminé!")
