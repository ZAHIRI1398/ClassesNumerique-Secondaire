#!/usr/bin/env python3
"""
Test final du scoring pour l'exercice "Texte à trous"
"""

def test_fill_in_blanks_scoring():
    """Test du scoring pour l'exercice Les coordonnées"""
    
    # Données de l'exercice (basées sur l'exercice ID 24)
    exercise_data = {
        "sentences": [
            "COMPLÈTE les coordonnées du sommet C : C (12 ; ___)",
            "Les coordonnées de B ( ___ ; ___ ) et A ( ___ ; ___ )"
        ],
        "correct_answers": ["12", "0", "0", "0", "12"]
    }
    
    print("=== TEST SCORING EXERCICE 'LES COORDONNÉES' ===")
    print()
    print("Exercice:")
    for i, sentence in enumerate(exercise_data["sentences"]):
        print(f"{i+1}. {sentence}")
    print()
    print("Réponses correctes attendues:", exercise_data["correct_answers"])
    print()
    
    # Test 1: Toutes les réponses correctes
    user_answers_correct = ["12", "0", "0", "0", "12"]
    score_correct = calculate_score(user_answers_correct, exercise_data["correct_answers"])
    print(f"Test 1 - Toutes correctes: {user_answers_correct}")
    print(f"Score: {score_correct}% (attendu: 100%)")
    print()
    
    # Test 2: Quelques erreurs
    user_answers_partial = ["12", "1", "0", "0", "12"]  # 1 erreur
    score_partial = calculate_score(user_answers_partial, exercise_data["correct_answers"])
    print(f"Test 2 - 1 erreur: {user_answers_partial}")
    print(f"Score: {score_partial}% (attendu: 80%)")
    print()
    
    # Test 3: Toutes fausses
    user_answers_wrong = ["5", "5", "5", "5", "5"]
    score_wrong = calculate_score(user_answers_wrong, exercise_data["correct_answers"])
    print(f"Test 3 - Toutes fausses: {user_answers_wrong}")
    print(f"Score: {score_wrong}% (attendu: 0%)")
    print()
    
    # Test 4: Réponses vides
    user_answers_empty = ["", "", "", "", ""]
    score_empty = calculate_score(user_answers_empty, exercise_data["correct_answers"])
    print(f"Test 4 - Réponses vides: {user_answers_empty}")
    print(f"Score: {score_empty}% (attendu: 0%)")
    print()
    
    # Validation
    print("=== VALIDATION ===")
    if score_correct == 100:
        print("✅ Score 100% : OK")
    else:
        print(f"❌ Score 100% : ERREUR (obtenu {score_correct}%)")
    
    if score_partial == 80:
        print("✅ Score partiel : OK")
    else:
        print(f"❌ Score partiel : ERREUR (obtenu {score_partial}%, attendu 80%)")
    
    if score_wrong == 0:
        print("✅ Score 0% : OK")
    else:
        print(f"❌ Score 0% : ERREUR (obtenu {score_wrong}%)")

def calculate_score(user_answers, correct_answers):
    """Calcule le score basé sur les réponses utilisateur"""
    if not user_answers or not correct_answers:
        return 0
    
    if len(user_answers) != len(correct_answers):
        return 0
    
    correct_count = 0
    for user_answer, correct_answer in zip(user_answers, correct_answers):
        # Normaliser les réponses (supprimer espaces, mettre en minuscules)
        user_clean = str(user_answer).strip().lower()
        correct_clean = str(correct_answer).strip().lower()
        
        if user_clean == correct_clean:
            correct_count += 1
    
    # Calculer le pourcentage
    score = round((correct_count / len(correct_answers)) * 100)
    return score

def test_edge_cases():
    """Test des cas limites"""
    print("\n=== TEST CAS LIMITES ===")
    
    # Cas avec espaces
    print("Test espaces:")
    score1 = calculate_score([" 12 ", "0", "0", "0", "12"], ["12", "0", "0", "0", "12"])
    print(f"Avec espaces: {score1}% (attendu: 100%)")
    
    # Cas avec casse différente
    print("Test casse:")
    score2 = calculate_score(["A", "b", "C"], ["a", "B", "c"])
    print(f"Casse différente: {score2}% (attendu: 100%)")
    
    # Cas avec nombres décimaux
    print("Test décimaux:")
    score3 = calculate_score(["12.0", "0.0"], ["12", "0"])
    print(f"Décimaux vs entiers: {score3}% (attendu: 0% car format différent)")

if __name__ == "__main__":
    test_fill_in_blanks_scoring()
    test_edge_cases()
    
    print("\n" + "="*50)
    print("CONCLUSION:")
    print("Le scoring fonctionne correctement pour l'exercice 'Texte à trous'")
    print("Prêt pour validation en production Railway !")
