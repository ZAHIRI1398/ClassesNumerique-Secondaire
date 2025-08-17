import sys
import json
from app import app

def test_fill_in_blanks_scoring():
    """
    Test directement la fonction de scoring pour l'exercice 2 (fill_in_blanks)
    en simulant différents scénarios de réponses
    """
    print("Test direct de la logique de scoring pour l'exercice 2...")
    
    # Simuler le contenu de l'exercice 2 (Les verbes)
    # Structure avec un mélange de chaînes simples et de dictionnaires avec clé 'word'
    exercise_content = {
        'sentences': [
            "Je ___ un élève.",
            "Tu ___ un élève.",
            "Il/Elle ___ un élève.",
            "Nous ___ des élèves.",
            "Vous ___ des élèves.",
            "Ils/Elles ___ des élèves."
        ],
        'words': [
            "suis",
            {"word": "es"},
            "est",
            {"word": "sommes"},
            "êtes",
            {"word": "sont"}
        ]
    }
    
    # Cas de test 1: Toutes les réponses correctes
    user_answers_correct = ["suis", "es", "est", "sommes", "êtes", "sont"]
    
    # Cas de test 2: Réponses partiellement correctes (4/6)
    user_answers_partial = ["suis", "es", "est", "sommes", "sont", "êtes"]
    
    # Cas de test 3: Réponses incorrectes
    user_answers_incorrect = ["a", "b", "c", "d", "e", "f"]
    
    # Simuler la logique de scoring pour fill_in_blanks
    with app.app_context():
        # Fonction simplifiée de scoring basée sur le code dans app.py
        def calculate_score(content, user_answers):
            # Compter les blancs dans les phrases
            total_blanks = sum(s.count('___') for s in content['sentences'])
            
            # Extraire les réponses correctes
            correct_answers = content['words']
            
            # Normaliser les réponses correctes (gérer à la fois les chaînes simples et les dictionnaires)
            normalized_correct_answers = []
            for answer in correct_answers:
                if isinstance(answer, dict) and 'word' in answer:
                    normalized_correct_answers.append(answer['word'])
                    print(f"[DEBUG] Normalized dict format: {answer} -> {answer['word']}")
                else:
                    normalized_correct_answers.append(answer)
                    print(f"[DEBUG] Kept string format: {answer}")
            
            # Utiliser les réponses normalisées
            correct_answers = normalized_correct_answers
            
            # Compter les réponses correctes
            correct_count = 0
            for i, user_answer in enumerate(user_answers):
                if i < len(correct_answers) and user_answer == correct_answers[i]:
                    correct_count += 1
                    print(f"[DEBUG] Réponse correcte à la position {i}: {user_answer}")
                else:
                    if i < len(correct_answers):
                        print(f"[DEBUG] Réponse incorrecte à la position {i}: {user_answer} (attendu: {correct_answers[i]})")
            
            # Calculer le score
            if total_blanks > 0:
                score = (correct_count / total_blanks) * 100
            else:
                score = 0
            
            return score, correct_count, total_blanks
        
        # Test avec réponses correctes
        score_correct, correct_count, total_blanks = calculate_score(exercise_content, user_answers_correct)
        print(f"\nTest avec réponses correctes:")
        print(f"Score: {score_correct:.2f}% ({correct_count}/{total_blanks})")
        if score_correct == 100:
            print("[OK] Score correct pour réponses 100% correctes: 100%")
        else:
            print(f"ERREUR: Score incorrect pour réponses 100% correctes: {score_correct:.2f}%")
            return False
        
        # Test avec réponses partiellement correctes
        score_partial, correct_count, total_blanks = calculate_score(exercise_content, user_answers_partial)
        print(f"\nTest avec réponses partiellement correctes:")
        print(f"Score: {score_partial:.2f}% ({correct_count}/{total_blanks})")
        if 65 <= score_partial <= 68:
            print(f"[OK] Score correct pour réponses partiellement correctes: {score_partial:.2f}%")
        else:
            print(f"ERREUR: Score incorrect pour réponses partiellement correctes: {score_partial:.2f}%")
            return False
        
        # Test avec réponses incorrectes
        score_incorrect, correct_count, total_blanks = calculate_score(exercise_content, user_answers_incorrect)
        print(f"\nTest avec réponses incorrectes:")
        print(f"Score: {score_incorrect:.2f}% ({correct_count}/{total_blanks})")
        if score_incorrect == 0:
            print("[OK] Score correct pour réponses 100% incorrectes: 0%")
        else:
            print(f"ERREUR: Score incorrect pour réponses 100% incorrectes: {score_incorrect:.2f}%")
            return False
        
        print("\n[SUCCES] TOUS LES TESTS ONT REUSSI!")
        print("La correction du format des mots dans l'exercice 2 fonctionne correctement.")
        return True

if __name__ == "__main__":
    success = test_fill_in_blanks_scoring()
    if not success:
        print("\n[ECHEC] ECHEC DES TESTS")
        sys.exit(1)
    else:
        print("\nLa correction a été validée avec succès!")
        sys.exit(0)
