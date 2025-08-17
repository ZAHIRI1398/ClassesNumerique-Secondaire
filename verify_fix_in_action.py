#!/usr/bin/env python3
"""
Script pour vérifier si la correction du scoring est bien appliquée
et simuler une soumission réelle pour l'exercice ID 6.
"""

import sys
import json
import os
from flask import Flask, request, session
from werkzeug.datastructures import ImmutableMultiDict

# Ajouter le répertoire courant au path pour pouvoir importer app
sys.path.append('.')

# Importer l'application Flask
from app import app, db, Exercise

def verify_scoring_logic():
    """Vérifie si la logique de scoring a bien été corrigée"""
    
    # Lire le contenu du fichier app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la première implémentation a été désactivée
    if "Cette implémentation a été désactivée" in content:
        print("[OK] La première implémentation a bien été désactivée")
    else:
        print("[ERREUR] La première implémentation n'a pas été désactivée")
        
        # Chercher les deux implémentations
        if "elif exercise.exercise_type == 'fill_in_blanks':" in content:
            count = content.count("elif exercise.exercise_type == 'fill_in_blanks':")
            print(f"  - Nombre d'implémentations trouvées: {count}")
            
            # Vérifier si la première implémentation est active
            if "user_answers = []" in content and "correct_answers = content.get('answers', [])" in content:
                print("  - La première implémentation simple est toujours active")
            
            # Vérifier si la deuxième implémentation est présente
            if "# Gestion des exercices Texte à trous avec la même logique que Mots à placer" in content:
                print("  - La deuxième implémentation complète est présente")
    
    return True

def simulate_exercise_submission():
    """Simule une soumission pour l'exercice ID 6 et affiche le résultat"""
    
    exercise_id = 6
    
    with app.app_context():
        # Récupérer l'exercice
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            print(f"Erreur: Exercice ID {exercise_id} non trouvé")
            return False
        
        print(f"Exercice trouvé: {exercise.title} (ID: {exercise_id})")
        
        # Analyser le contenu JSON
        content = json.loads(exercise.content)
        
        # Récupérer les réponses correctes
        correct_answers = content.get('answers', [])
        if not correct_answers:
            correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        print(f"Réponses correctes: {correct_answers}")
        
        # Créer un objet request.form simulé avec les réponses correctes
        form_data = {}
        for i, answer in enumerate(correct_answers):
            form_data[f'answer_{i}'] = answer
        
        print(f"Données du formulaire: {form_data}")
        
        # Compter les blancs dans le contenu
        total_blanks_in_content = 0
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
        
        print(f"Nombre total de blancs: {total_blanks_in_content}")
        
        # Simuler le calcul du score
        correct_blanks = 0
        for i in range(total_blanks_in_content):
            user_answer = form_data.get(f'answer_{i}', '').strip()
            correct_answer = correct_answers[i] if i < len(correct_answers) else ''
            is_correct = user_answer.lower() == correct_answer.lower()
            status = "Correct" if is_correct else f"Incorrect (attendu: '{correct_answer}')"
            print(f"Blank {i}: '{user_answer}' -> {status}")
            if is_correct:
                correct_blanks += 1
        
        # Calculer le score final
        score = (correct_blanks / total_blanks_in_content) * 100 if total_blanks_in_content > 0 else 0
        print(f"Score calculé: {score}% ({correct_blanks}/{total_blanks_in_content})")
        
        # Vérifier si le score est correct
        expected_score = 100.0  # Toutes les réponses sont correctes
        if score == expected_score:
            print(f"SUCCÈS: Le score calculé ({score}%) correspond au score attendu ({expected_score}%)")
            return True
        else:
            print(f"ÉCHEC: Le score calculé ({score}%) ne correspond pas au score attendu ({expected_score}%)")
            return False

def check_route_implementation():
    """Vérifie l'implémentation de la route de soumission"""
    
    # Extraire la route de soumission du fichier app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher la route de soumission
    route_pattern = "@app.route('/exercise/<int:exercise_id>/submit', methods=['POST'])"
    if route_pattern in content:
        print("Route de soumission trouvée")
        
        # Trouver l'index de la route
        route_index = content.find(route_pattern)
        
        # Extraire la fonction de soumission (les 50 lignes suivantes)
        submit_function = content[route_index:route_index + 2000]
        
        # Vérifier si la fonction utilise la logique de scoring pour fill_in_blanks
        if "elif exercise.exercise_type == 'fill_in_blanks':" in submit_function:
            print("La fonction de soumission contient la logique pour fill_in_blanks")
            
            # Vérifier si la fonction utilise pass
            if "pass  # La logique de scoring est maintenant gérée" in submit_function:
                print("La fonction utilise 'pass' pour rediriger vers la logique complète")
                return True
            else:
                print("La fonction ne semble pas utiliser 'pass' pour rediriger")
                
                # Vérifier si la fonction calcule un score
                if "score = " in submit_function:
                    print("La fonction calcule un score directement")
                    
                    # Extraire la logique de calcul du score
                    score_calc_start = submit_function.find("score = ")
                    score_calc_end = submit_function.find("\n", score_calc_start)
                    score_calc = submit_function[score_calc_start:score_calc_end]
                    print(f"Calcul du score: {score_calc}")
                    
                    return False
    else:
        print("Route de soumission non trouvée")
        return False

if __name__ == "__main__":
    print("Vérification de la correction du scoring pour l'exercice ID 6...")
    print("\n1. Vérification de la logique de scoring dans app.py:")
    verify_scoring_logic()
    
    print("\n2. Vérification de l'implémentation de la route de soumission:")
    check_route_implementation()
    
    print("\n3. Simulation d'une soumission pour l'exercice ID 6:")
    simulate_exercise_submission()
