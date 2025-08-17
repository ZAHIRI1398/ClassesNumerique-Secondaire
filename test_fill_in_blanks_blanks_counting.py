#!/usr/bin/env python3
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
            print(f"\nExercice: {exercise.title} (ID: {exercise.id})")
            
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
                print(f"  [PROBLEME] INCOHÉRENCE: {total_blanks_in_content} blancs vs {len(correct_answers)} réponses")
            else:
                print(f"  [OK] Cohérent: {total_blanks_in_content} blancs = {len(correct_answers)} réponses")

if __name__ == '__main__':
    test_blanks_counting()
