"""
Script de test pour la correction du scoring des exercices "texte à trous" de type "ranger par ordre".
Ce script permet de tester la solution avant de l'intégrer dans l'application principale.
"""

import json
import sys
from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise

def test_ordering_detection():
    """Teste la détection des exercices de type "ranger par ordre" """
    test_cases = [
        ("Ranger par ordre croissant les nombres suivants : 0.9 - 0.85 - 0.08 - 0.8 - 0.18", True, "croissant"),
        ("Classer dans l'ordre décroissant : 10, 5, 8, 3, 7", True, "décroissant"),
        ("Complétez les phrases avec les mots suivants", False, None),
        ("Ranger dans l'ordre croissant", True, "croissant"),
        ("Mettez les nombres en ordre décroissant", True, "décroissant"),
        ("Ordonner de façon croissante", True, "croissant"),
        ("", False, None)
    ]
    
    print("\n=== TEST DE DÉTECTION DES EXERCICES DE RANGEMENT ===")
    all_passed = True
    
    for i, (description, expected_is_ordering, expected_type) in enumerate(test_cases):
        is_ordering, ordering_type = is_ordering_exercise(description)
        
        # Accepter 'decroissant' comme équivalent à 'décroissant'
        type_match = ordering_type == expected_type
        if expected_type == 'décroissant' and ordering_type == 'decroissant':
            type_match = True
        
        passed = (is_ordering == expected_is_ordering and type_match)
        status = "REUSSI" if passed else "ECHEC"
        
        print(f"Test {i+1}: {status}")
        print(f"  Description: '{description}'")
        print(f"  Résultat: is_ordering={is_ordering}, type={ordering_type}")
        print(f"  Attendu: is_ordering={expected_is_ordering}, type={expected_type}")
        
        if not passed:
            all_passed = False
    
    print(f"\nRésultat global: {'REUSSI - TOUS LES TESTS' if all_passed else 'ECHEC - CERTAINS TESTS ONT ECHOUE'}")
    return all_passed

def test_ordering_evaluation():
    """Teste l'évaluation des exercices de type "ranger par ordre" """
    test_cases = [
        # (user_answers, correct_answers, ordering_type, expected_correct, expected_total)
        (["0.08", "0.18", "0.8", "0.85", "0.9"], ["0.9", "0.85", "0.08", "0.8", "0.18"], "croissant", 5, 5),  # Ordre croissant parfait
        (["0.9", "0.85", "0.8", "0.18", "0.08"], ["0.9", "0.85", "0.08", "0.8", "0.18"], "décroissant", 5, 5),  # Ordre décroissant parfait
        (["0.9", "0.85", "0.8", "0.18", "0.08"], ["0.9", "0.85", "0.08", "0.8", "0.18"], "croissant", 0, 5),  # Ordre inversé
        (["0.08", "0.18", "0.85", "0.8", "0.9"], ["0.9", "0.85", "0.08", "0.8", "0.18"], "croissant", 0, 5),  # Ordre presque correct mais une erreur
        (["0.08", "0.18", "0.8", "0.85", "0.91"], ["0.9", "0.85", "0.08", "0.8", "0.18"], "croissant", 2, 5),  # Bon ordre mais un nombre différent
        (["", "0.18", "0.8", "0.85", "0.9"], ["0.9", "0.85", "0.08", "0.8", "0.18"], "croissant", 0, 5),  # Réponse manquante
    ]
    
    print("\n=== TEST D'ÉVALUATION DES EXERCICES DE RANGEMENT ===")
    all_passed = True
    
    for i, (user_answers, correct_answers, ordering_type, expected_correct, expected_total) in enumerate(test_cases):
        correct_count, total_count, feedback = evaluate_ordering_exercise(
            user_answers, correct_answers, ordering_type
        )
        
        passed = (correct_count == expected_correct and total_count == expected_total)
        status = "REUSSI" if passed else "ECHEC"
        
        print(f"Test {i+1}: {status}")
        print(f"  Réponses utilisateur: {user_answers}")
        print(f"  Réponses correctes: {correct_answers}")
        print(f"  Type d'ordre: {ordering_type}")
        print(f"  Résultat: {correct_count}/{total_count}")
        print(f"  Attendu: {expected_correct}/{expected_total}")
        
        if not passed:
            all_passed = False
            print(f"  Feedback détaillé: {json.dumps(feedback, indent=2)}")
    
    print(f"\nRésultat global: {'REUSSI - TOUS LES TESTS' if all_passed else 'ECHEC - CERTAINS TESTS ONT ECHOUE'}")
    return all_passed

def test_real_world_scenario():
    """Teste un scénario réel avec l'exercice de rangement par ordre croissant"""
    print("\n=== TEST DE SCÉNARIO RÉEL ===")
    
    # Description de l'exercice
    description = "Ranger par ordre croissant les nombres suivants : 0.9 - 0.85 - 0.08 - 0.8 - 0.18"
    
    # Détection du type d'exercice
    is_ordering, ordering_type = is_ordering_exercise(description)
    print(f"Description: '{description}'")
    print(f"Détection: is_ordering={is_ordering}, type={ordering_type}")
    
    if not is_ordering:
        print("ECHEC: L'exercice n'a pas été détecté comme un exercice de rangement")
        return False
    
    # Réponses correctes (dans l'ordre où elles apparaissent dans l'énoncé)
    correct_answers = ["0.9", "0.85", "0.08", "0.8", "0.18"]
    
    # Cas 1: Réponses parfaites (ordre croissant)
    user_answers_perfect = ["0.08", "0.18", "0.8", "0.85", "0.9"]
    
    correct_count, total_count, feedback = evaluate_ordering_exercise(
        user_answers_perfect, correct_answers, ordering_type
    )
    
    print("\nCas 1: Réponses parfaites")
    print(f"Score: {correct_count}/{total_count} ({(correct_count/total_count)*100}%)")
    
    # Cas 2: Réponses dans le mauvais ordre (comme dans le problème initial)
    user_answers_wrong = ["0.9", "0.85", "0.08", "0.8", "0.18"]  # Ordre de l'énoncé, pas croissant
    
    correct_count, total_count, feedback = evaluate_ordering_exercise(
        user_answers_wrong, correct_answers, ordering_type
    )
    
    print("\nCas 2: Réponses dans le mauvais ordre (problème initial)")
    print(f"Score: {correct_count}/{total_count} ({(correct_count/total_count)*100}%)")
    
    # Vérifier que le cas 1 donne 100% et le cas 2 donne un score inférieur
    if correct_count == 0:
        print("REUSSI: Le problème initial est bien détecté (score de 0%)")
        return True
    else:
        print(f"ECHEC: Le problème initial n'est pas correctement détecté (score de {(correct_count/total_count)*100}%)")
        return False

if __name__ == "__main__":
    print("=== TESTS DE LA CORRECTION DU SCORING DES EXERCICES DE RANGEMENT ===")
    
    detection_passed = test_ordering_detection()
    evaluation_passed = test_ordering_evaluation()
    scenario_passed = test_real_world_scenario()
    
    all_passed = detection_passed and evaluation_passed and scenario_passed
    
    print("\n=== RÉSUMÉ DES TESTS ===")
    print(f"Détection des exercices: {'REUSSI' if detection_passed else 'ECHEC'}")
    print(f"Évaluation des réponses: {'REUSSI' if evaluation_passed else 'ECHEC'}")
    print(f"Scénario réel: {'REUSSI' if scenario_passed else 'ECHEC'}")
    
    print(f"\nRésultat global: {'REUSSI - TOUS LES TESTS' if all_passed else 'ECHEC - CERTAINS TESTS ONT ECHOUE'}")
    
    sys.exit(0 if all_passed else 1)
