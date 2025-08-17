"""
Script de test autonome pour vérifier la logique de scoring des exercices fill_in_blanks,
en particulier pour les exercices de rangement par ordre croissant ou décroissant.
"""

import json
import re
from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise

def test_standard_fill_in_blanks():
    """Test de la logique de scoring standard pour les exercices fill_in_blanks"""
    print("\n=== Test de la logique de scoring standard ===")
    
    # Cas de test 1: Toutes les réponses correctes
    user_answers = ["Paris", "France", "Europe"]
    correct_answers = ["Paris", "France", "Europe"]
    
    correct_count = sum(1 for ua, ca in zip(user_answers, correct_answers) if ua.lower() == ca.lower())
    total_count = len(correct_answers)
    score = (correct_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"Cas 1 - Toutes correctes:")
    print(f"  - Réponses utilisateur: {user_answers}")
    print(f"  - Réponses correctes: {correct_answers}")
    print(f"  - Score: {correct_count}/{total_count} ({score}%)")
    
    # Cas de test 2: Certaines réponses correctes
    user_answers = ["Paris", "Allemagne", "Europe"]
    correct_answers = ["Paris", "France", "Europe"]
    
    correct_count = sum(1 for ua, ca in zip(user_answers, correct_answers) if ua.lower() == ca.lower())
    total_count = len(correct_answers)
    score = (correct_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\nCas 2 - Partiellement correctes:")
    print(f"  - Réponses utilisateur: {user_answers}")
    print(f"  - Réponses correctes: {correct_answers}")
    print(f"  - Score: {correct_count}/{total_count} ({score}%)")
    
    # Cas de test 3: Aucune réponse correcte
    user_answers = ["Londres", "Allemagne", "Asie"]
    correct_answers = ["Paris", "France", "Europe"]
    
    correct_count = sum(1 for ua, ca in zip(user_answers, correct_answers) if ua.lower() == ca.lower())
    total_count = len(correct_answers)
    score = (correct_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\nCas 3 - Aucune correcte:")
    print(f"  - Réponses utilisateur: {user_answers}")
    print(f"  - Réponses correctes: {correct_answers}")
    print(f"  - Score: {correct_count}/{total_count} ({score}%)")

def test_ordering_exercises():
    """Test de la logique de scoring pour les exercices de rangement"""
    print("\n=== Test de la logique de scoring pour exercices de rangement ===")
    
    # Test de détection des exercices de rangement
    test_descriptions = [
        "Ranger par ordre croissant les nombres suivants : 0.9 - 0.85 - 0.08 - 0.8 - 0.18",
        "Classer dans l'ordre decroissant : 10, 5, 8, 3, 7",
        "Complétez les phrases avec les mots suivants",
        "Ranger dans l'ordre croissant"
    ]
    
    for desc in test_descriptions:
        is_ordering, order_type = is_ordering_exercise(desc)
        print(f"Description: '{desc}'")
        print(f"  - Est un exercice de rangement: {is_ordering}")
        print(f"  - Type d'ordre: {order_type}")
    
    # Test d'évaluation - Ordre croissant correct
    print("\n--- Test d'évaluation - Ordre croissant ---")
    user_answers = ["0.08", "0.18", "0.8", "0.85", "0.9"]  # Ordre croissant correct
    correct_answers = ["0.08", "0.18", "0.8", "0.85", "0.9"]  # Même ordre (pour vérifier all_numbers_present)
    
    correct_count, total_count, feedback = evaluate_ordering_exercise(
        user_answers, correct_answers, 'croissant'
    )
    
    print(f"Cas 1 - Ordre croissant correct:")
    print(f"  - Réponses utilisateur: {user_answers}")
    print(f"  - Réponses correctes: {correct_answers}")
    print(f"  - Score: {correct_count}/{total_count} ({(correct_count/total_count)*100 if total_count > 0 else 0}%)")
    
    # Test d'évaluation - Ordre décroissant correct
    print("\n--- Test d'évaluation - Ordre décroissant ---")
    user_answers = ["10", "8", "7", "5", "3"]  # Ordre décroissant correct
    correct_answers = ["3", "5", "7", "8", "10"]  # Ordre croissant (pour vérifier all_numbers_present)
    
    correct_count, total_count, feedback = evaluate_ordering_exercise(
        user_answers, correct_answers, 'decroissant'
    )
    
    print(f"Cas 2 - Ordre décroissant correct:")
    print(f"  - Réponses utilisateur: {user_answers}")
    print(f"  - Réponses correctes: {correct_answers}")
    print(f"  - Score: {correct_count}/{total_count} ({(correct_count/total_count)*100 if total_count > 0 else 0}%)")
    
    # Test d'évaluation - Ordre incorrect
    print("\n--- Test d'évaluation - Ordre incorrect ---")
    user_answers = ["0.9", "0.08", "0.18", "0.8", "0.85"]  # Ordre mélangé
    correct_answers = ["0.08", "0.18", "0.8", "0.85", "0.9"]  # Ordre croissant
    
    correct_count, total_count, feedback = evaluate_ordering_exercise(
        user_answers, correct_answers, 'croissant'
    )
    
    print(f"Cas 3 - Ordre incorrect:")
    print(f"  - Réponses utilisateur: {user_answers}")
    print(f"  - Réponses correctes: {correct_answers}")
    print(f"  - Score: {correct_count}/{total_count} ({(correct_count/total_count)*100 if total_count > 0 else 0}%)")
    
    # Test d'évaluation - Réponses incomplètes
    print("\n--- Test d'évaluation - Réponses incomplètes ---")
    user_answers = ["0.08", "", "0.8", "0.85", "0.9"]  # Une réponse vide
    correct_answers = ["0.08", "0.18", "0.8", "0.85", "0.9"]  # Ordre croissant
    
    correct_count, total_count, feedback = evaluate_ordering_exercise(
        user_answers, correct_answers, 'croissant'
    )
    
    print(f"Cas 4 - Réponses incomplètes:")
    print(f"  - Réponses utilisateur: {user_answers}")
    print(f"  - Réponses correctes: {correct_answers}")
    print(f"  - Score: {correct_count}/{total_count} ({(correct_count/total_count)*100 if total_count > 0 else 0}%)")

def test_counting_blanks():
    """Test du comptage des blanks dans les exercices fill_in_blanks"""
    print("\n=== Test du comptage des blanks ===")
    
    # Cas 1: Contenu avec 'sentences'
    content_with_sentences = {
        'sentences': [
            "Paris est la capitale de la ___.",
            "La ___ est un pays d'Europe.",
            "L'___ est un continent."
        ]
    }
    
    total_blanks = 0
    if 'sentences' in content_with_sentences:
        sentences_blanks = sum(s.count('___') for s in content_with_sentences['sentences'])
        total_blanks = sentences_blanks
    elif 'text' in content_with_sentences:
        text_blanks = content_with_sentences['text'].count('___')
        total_blanks = text_blanks
    
    print(f"Cas 1 - Contenu avec 'sentences':")
    print(f"  - Contenu: {content_with_sentences}")
    print(f"  - Total blanks: {total_blanks}")
    
    # Cas 2: Contenu avec 'text'
    content_with_text = {
        'text': "Paris est la capitale de la ___. La ___ est un pays d'Europe. L'___ est un continent."
    }
    
    total_blanks = 0
    if 'sentences' in content_with_text:
        sentences_blanks = sum(s.count('___') for s in content_with_text['sentences'])
        total_blanks = sentences_blanks
    elif 'text' in content_with_text:
        text_blanks = content_with_text['text'].count('___')
        total_blanks = text_blanks
    
    print(f"\nCas 2 - Contenu avec 'text':")
    print(f"  - Contenu: {content_with_text}")
    print(f"  - Total blanks: {total_blanks}")
    
    # Cas 3: Contenu avec 'sentences' et 'text' (priorité à 'sentences')
    content_with_both = {
        'sentences': [
            "Paris est la capitale de la ___.",
            "La ___ est un pays d'Europe.",
            "L'___ est un continent."
        ],
        'text': "Paris est la capitale de la ___. La ___ est un pays d'Europe. L'___ est un continent."
    }
    
    total_blanks = 0
    if 'sentences' in content_with_both:
        sentences_blanks = sum(s.count('___') for s in content_with_both['sentences'])
        total_blanks = sentences_blanks
    elif 'text' in content_with_both:
        text_blanks = content_with_both['text'].count('___')
        total_blanks = text_blanks
    
    print(f"\nCas 3 - Contenu avec 'sentences' et 'text' (priorité à 'sentences'):")
    print(f"  - Contenu: {content_with_both}")
    print(f"  - Total blanks: {total_blanks}")

if __name__ == "__main__":
    print("=== Tests de la logique de scoring des exercices fill_in_blanks ===")
    test_standard_fill_in_blanks()
    test_ordering_exercises()
    test_counting_blanks()
    print("\n=== Fin des tests ===")
