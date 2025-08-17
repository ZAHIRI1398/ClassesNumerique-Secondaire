"""
Solution pour corriger le scoring des exercices "texte à trous" de type "ranger par ordre croissant/décroissant".
Ce script contient les fonctions nécessaires pour détecter et traiter correctement ces exercices.
"""

def is_ordering_exercise(exercise_description):
    """
    Détecte si un exercice est de type "ranger par ordre croissant/décroissant"
    
    Args:
        exercise_description (str): Description de l'exercice
        
    Returns:
        tuple: (is_ordering, ordering_type) où ordering_type est 'croissant' ou 'décroissant'
    """
    if not exercise_description:
        return False, None
        
    description_lower = exercise_description.lower()
    
    if 'ranger' in description_lower and 'ordre' in description_lower:
        if 'croissant' in description_lower:
            return True, 'croissant'
        elif 'décroissant' in description_lower or 'decroissant' in description_lower:
            return True, 'décroissant'
    
    return False, None

def evaluate_ordering_exercise(user_answers, correct_answers, ordering_type):
    """
    Évalue les réponses d'un exercice de type "ranger par ordre"
    
    Args:
        user_answers (list): Liste des réponses de l'utilisateur
        correct_answers (list): Liste des réponses correctes
        ordering_type (str): 'croissant' ou 'décroissant'
        
    Returns:
        tuple: (correct_count, total_count, feedback_details)
    """
    total_count = len(user_answers)
    feedback_details = []
    
    try:
        # Convertir en nombres flottants
        user_numbers = [float(ans) for ans in user_answers if ans.strip()]
        correct_numbers = [float(ans) for ans in correct_answers if ans.strip()]
        
        # Vérifier si les nombres sont dans le bon ordre
        is_correct_order = False
        if ordering_type == 'croissant':
            is_correct_order = all(user_numbers[i] <= user_numbers[i+1] for i in range(len(user_numbers)-1))
        else:  # décroissant
            is_correct_order = all(user_numbers[i] >= user_numbers[i+1] for i in range(len(user_numbers)-1))
        
        # Vérifier si tous les nombres attendus sont présents
        all_numbers_present = set(user_numbers) == set(correct_numbers)
        
        # Calculer le score
        correct_count = 0
        if is_correct_order and all_numbers_present:
            correct_count = total_count
        elif is_correct_order:
            correct_count = total_count // 2  # Donner la moitié des points si l'ordre est bon mais pas les nombres
        
        # Créer le feedback pour chaque réponse
        for i in range(total_count):
            user_answer = user_answers[i] if i < len(user_answers) else ''
            correct_answer = correct_answers[i] if i < len(correct_answers) else ''
            
            # Déterminer si cette position est correcte
            position_correct = is_correct_order and all_numbers_present
            
            feedback_details.append({
                'blank_index': i,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': position_correct,
                'status': 'Correct' if position_correct else f'Attendu: ordre {ordering_type}',
                'sentence_index': -1
            })
            
    except (ValueError, TypeError) as e:
        # En cas d'erreur, retourner 0 correct
        print(f"Erreur lors de la conversion en nombres: {e}")
        correct_count = 0
        
    return correct_count, total_count, feedback_details

# Exemple d'utilisation:
if __name__ == "__main__":
    # Test avec un exercice de type "ranger par ordre croissant"
    description = "Ranger par ordre croissant : 0.9 - 0.85 - 0.08 - 0.8 - 0.18"
    is_ordering, ordering_type = is_ordering_exercise(description)
    
    if is_ordering:
        print(f"Détecté exercice de type 'ranger par ordre {ordering_type}'")
        
        # Simuler des réponses utilisateur
        user_answers = ["0.08", "0.18", "0.8", "0.85", "0.9"]  # Réponses correctes
        correct_answers = ["0.08", "0.18", "0.8", "0.85", "0.9"]
        
        correct_count, total_count, feedback = evaluate_ordering_exercise(
            user_answers, correct_answers, ordering_type
        )
        
        print(f"Score: {correct_count}/{total_count} ({(correct_count/total_count)*100}%)")
        print(f"Feedback: {feedback}")
        
        # Test avec des réponses dans le mauvais ordre
        user_answers_wrong = ["0.9", "0.85", "0.8", "0.18", "0.08"]  # Ordre décroissant au lieu de croissant
        correct_count, total_count, feedback = evaluate_ordering_exercise(
            user_answers_wrong, correct_answers, ordering_type
        )
        
        print(f"Score (mauvais ordre): {correct_count}/{total_count} ({(correct_count/total_count)*100}%)")
