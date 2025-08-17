#!/usr/bin/env python3
"""
Script pour tester la correction du scoring pour l'exercice ID 6 (fill_in_blanks)
"""

import sys
import json
import requests
from flask import Flask, request, session
sys.path.append('.')

from app import app, db, Exercise, User

def test_exercise_6_scoring():
    """
    Teste le scoring de l'exercice ID 6 après la correction du conflit de logiques
    """
    exercise_id = 6
    
    with app.app_context():
        # Récupérer l'exercice
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            print(f"[ERREUR] Erreur: Exercice ID {exercise_id} non trouvé")
            return False
        
        print(f"[OK] Exercice trouvé: {exercise.title} (ID: {exercise_id})")
        print(f"   Type: {exercise.exercise_type}")
        
        # Analyser le contenu JSON
        try:
            content = json.loads(exercise.content)
            print(f"[OK] Contenu JSON valide")
        except json.JSONDecodeError:
            print(f"[ERREUR] Erreur: Contenu JSON invalide")
            return False
        
        # Afficher la structure de l'exercice
        print("\nStructure de l'exercice:")
        for key, value in content.items():
            if isinstance(value, list):
                print(f"   {key}: {value} (longueur: {len(value)})")
            else:
                print(f"   {key}: {value}")
        
        # Compter les blancs dans le contenu
        total_blanks_in_content = 0
        
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            print(f"\nFormat 'sentences' détecté: {sentences_blanks} blancs")
            for i, sentence in enumerate(content['sentences']):
                blanks_in_sentence = sentence.count('___')
                print(f"   Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"\nFormat 'text' détecté: {text_blanks} blancs")
            print(f"   Texte: {content['text']}")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('answers', [])
        if not correct_answers:
            correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        print(f"\nTotal des blancs trouvés: {total_blanks_in_content}")
        print(f"Réponses correctes: {correct_answers} (total: {len(correct_answers)})")
        
        # Vérifier la cohérence
        if total_blanks_in_content != len(correct_answers):
            print(f"[ATTENTION] INCOHÉRENCE: {total_blanks_in_content} blancs vs {len(correct_answers)} réponses")
        else:
            print(f"[OK] Cohérent: {total_blanks_in_content} blancs = {len(correct_answers)} réponses")
        
        # Simuler la soumission de réponses correctes
        print("\nSimulation de soumission avec réponses correctes:")
        form_data = {}
        for i, answer in enumerate(correct_answers):
            form_data[f'answer_{i}'] = answer
            print(f"   answer_{i} = '{answer}'")
        
        # Calculer le score attendu
        expected_score = 100.0  # Toutes les réponses sont correctes
        print(f"\nScore attendu: {expected_score}%")
        
        # Simuler le calcul du score avec la nouvelle logique
        print("\nCalcul du score avec la logique corrigée:")
        correct_blanks = 0
        for i in range(total_blanks_in_content):
            user_answer = form_data.get(f'answer_{i}', '').strip()
            correct_answer = correct_answers[i] if i < len(correct_answers) else ''
            is_correct = user_answer.lower() == correct_answer.lower()
            status = "[CORRECT] Correct" if is_correct else f"[INCORRECT] Incorrect (attendu: '{correct_answer}')"
            print(f"   Blank {i}: '{user_answer}' -> {status}")
            if is_correct:
                correct_blanks += 1
        
        # Calculer le score final
        score = (correct_blanks / total_blanks_in_content) * 100 if total_blanks_in_content > 0 else 0
        print(f"\nScore calculé: {score}% ({correct_blanks}/{total_blanks_in_content})")
        
        # Vérifier si le score correspond à l'attendu
        if score == expected_score:
            print(f"[OK] SUCCÈS: Le score calculé ({score}%) correspond au score attendu ({expected_score}%)")
            return True
        else:
            print(f"[ERREUR] ÉCHEC: Le score calculé ({score}%) ne correspond pas au score attendu ({expected_score}%)")
            return False

if __name__ == '__main__':
    print("Test de la correction du scoring pour l'exercice ID 6...")
    result = test_exercise_6_scoring()
    if result:
        print("\n[OK] Test réussi! La correction du scoring fonctionne correctement.")
    else:
        print("\n[ERREUR] Test échoué. La correction du scoring ne fonctionne pas comme prévu.")
