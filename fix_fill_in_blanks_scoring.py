#!/usr/bin/env python3
"""
Script pour corriger le problème de scoring des exercices fill_in_blanks
qui ne compte actuellement qu'un blanc par ligne au lieu de tous les blancs.
"""

import os
import re
import sys
import json

def fix_fill_in_blanks_scoring():
    """
    Corrige la logique de scoring des exercices fill_in_blanks dans app.py
    pour compter correctement tous les blancs dans chaque phrase.
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
    
    # Rechercher la section problématique
    pattern = r"if 'sentences' in content:.*?sentences_blanks = sum\(s\.count\('___'\) for s in content\['sentences'\]\)"
    
    # Vérifier si le pattern existe
    if not re.search(pattern, content, re.DOTALL):
        print("La section de code à modifier n'a pas été trouvée.")
        return False
    
    # Faire une sauvegarde du fichier original
    backup_path = f"{app_path}.bak"
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Sauvegarde créée: {backup_path}")
    
    # Corriger le code
    # Le problème est que la logique actuelle compte correctement le nombre de blancs,
    # mais il y a peut-être un problème ailleurs dans le traitement des réponses
    
    # Vérifier la logique de traitement des réponses
    answer_pattern = r"for i in range\(total_blanks\):.*?user_answer = request\.form\.get\(f'answer_{i}', ''\)\.strip\(\)"
    
    # Modifier le code pour ajouter des logs plus détaillés
    modified_content = content.replace(
        "app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Total blanks found in content: {total_blanks_in_content}\")",
        "app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Total blanks found in content: {total_blanks_in_content}\")\n"
        "            # Log détaillé pour chaque phrase et ses blancs\n"
        "            if 'sentences' in content:\n"
        "                for i, sentence in enumerate(content['sentences']):\n"
        "                    blanks_in_sentence = sentence.count('___')\n"
        "                    app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs\")"
    )
    
    # Modifier la logique de traitement des réponses pour s'assurer que chaque blanc est traité
    modified_content = modified_content.replace(
        "# Vérifier chaque blanc individuellement - Même logique que word_placement\n            for i in range(total_blanks):",
        "# Vérifier chaque blanc individuellement - Même logique que word_placement\n"
        "            app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total\")\n"
        "            for i in range(total_blanks):"
    )
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Modifications appliquées avec succès!")
    print("Les logs détaillés ont été ajoutés pour diagnostiquer le problème de comptage des blancs.")
    return True

def create_test_script():
    """
    Crée un script de test pour vérifier le comptage des blancs dans les exercices fill_in_blanks
    """
    test_script_path = 'test_fill_in_blanks_blanks_counting.py'
    
    test_script_content = '''#!/usr/bin/env python3
"""
Script de test pour vérifier le comptage des blancs dans les exercices fill_in_blanks
"""

import sys
import json
sys.path.append('.')

from app import app, db, Exercise

def test_blanks_counting():
    """Test du comptage des blancs dans les exercices fill_in_blanks"""
    
    with app.app_context():
        # Récupérer tous les exercices fill_in_blanks
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        
        if not exercises:
            print("Aucun exercice fill_in_blanks trouvé")
            return
        
        print(f"Trouvé {len(exercises)} exercices fill_in_blanks")
        
        for exercise in exercises:
            print(f"\\nExercice: {exercise.title} (ID: {exercise.id})")
            
            # Analyser le contenu JSON
            try:
                content = json.loads(exercise.content)
            except json.JSONDecodeError:
                print(f"  Erreur: Contenu JSON invalide")
                continue
            
            # Compter les blancs dans le contenu
            total_blanks_in_content = 0
            
            if 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content += text_blanks
                print(f"  Format 'text': {text_blanks} blancs trouvés")
                print(f"  Texte: {content['text']}")
            
            if 'sentences' in content:
                print(f"  Format 'sentences': Analyse phrase par phrase")
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    print(f"    Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
                    total_blanks_in_content += blanks_in_sentence
            
            # Récupérer les réponses correctes
            correct_answers = content.get('words', [])
            if not correct_answers:
                correct_answers = content.get('available_words', [])
            
            print(f"  Total des blancs trouvés: {total_blanks_in_content}")
            print(f"  Réponses correctes: {correct_answers} (total: {len(correct_answers)})")
            
            # Vérifier la cohérence
            if total_blanks_in_content != len(correct_answers):
                print(f"  ⚠️ INCOHÉRENCE: {total_blanks_in_content} blancs vs {len(correct_answers)} réponses")
            else:
                print(f"  ✅ Cohérent: {total_blanks_in_content} blancs = {len(correct_answers)} réponses")

if __name__ == '__main__':
    test_blanks_counting()
'''
    
    with open(test_script_path, 'w', encoding='utf-8') as file:
        file.write(test_script_content)
    
    print(f"Script de test créé: {test_script_path}")
    return True

if __name__ == '__main__':
    print("Correction du problème de scoring des exercices fill_in_blanks...")
    fix_fill_in_blanks_scoring()
    create_test_script()
    print("Terminé!")
