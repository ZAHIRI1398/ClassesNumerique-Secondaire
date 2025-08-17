#!/usr/bin/env python3
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
            print(f"\n{'='*50}")
            result = simulate_scoring(exercise.id)
            all_ok = all_ok and result
        
        if all_ok:
            print("\n[SUCCÈS] Tous les exercices sont cohérents!")
        else:
            print("\n[ÉCHEC] Certains exercices présentent des incohérences.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Tester un exercice spécifique
        exercise_id = int(sys.argv[1])
        simulate_scoring(exercise_id)
    else:
        # Tester tous les exercices
        test_all_exercises()
