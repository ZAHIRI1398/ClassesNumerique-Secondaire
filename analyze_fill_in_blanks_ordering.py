"""
Script d'analyse et de correction pour les exercices "texte à trous" de type "ranger par ordre".

Ce script permet de détecter et d'évaluer correctement les exercices qui demandent
de ranger des nombres par ordre croissant ou decroissant.
"""

import re
import json
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('analyze_fill_in_blanks_ordering.log')
    ]
)
logger = logging.getLogger(__name__)

def is_ordering_exercise(description):
    """
    Détecte si un exercice est de type "ranger par ordre croissant/decroissant"
    
    Args:
        description (str): Description de l'exercice
        
    Returns:
        tuple: (is_ordering, ordering_type) où ordering_type est 'croissant' ou 'decroissant'
    """
    if not description:
        return False, None
        
    description_lower = description.lower()
    
    # Patterns à rechercher
    patterns = [
        # Patterns pour ordre décroissant (vérifiés en premier pour éviter les faux positifs)
        (r'ranger.*ordre.*d[ée]croissant', 'decroissant'),
        (r'classer.*ordre.*d[ée]croissant', 'decroissant'),
        (r'ordonner.*d[ée]croissant', 'decroissant'),
        (r'ordre.*d[ée]croissant', 'decroissant'),
        (r'mettez.*ordre.*d[ée]croissant', 'decroissant'),
        (r'd[ée]croissant', 'decroissant'),
        
        # Patterns pour ordre croissant
        (r'ranger.*ordre.*croissant', 'croissant'),
        (r'classer.*ordre.*croissant', 'croissant'),
        (r'ordonner.*croissant', 'croissant'),
        (r'ordre.*croissant', 'croissant'),
        (r'croissant', 'croissant')
    ]
    
    for pattern, order_type in patterns:
        if re.search(pattern, description_lower):
            logger.info(f"Détecté exercice de type 'ranger par ordre {order_type}' avec pattern '{pattern}'")
            return True, order_type
    
    return False, None

def evaluate_ordering_exercise(user_answers, correct_answers, ordering_type):
    """
    Évalue les réponses d'un exercice de type "ranger par ordre"
    
    Args:
        user_answers (list): Liste des réponses de l'utilisateur
        correct_answers (list): Liste des réponses correctes
        ordering_type (str): 'croissant' ou 'decroissant'
        
    Returns:
        tuple: (correct_count, total_count, feedback_details)
    """
    total_count = len(user_answers)
    feedback_details = []
    
    try:
        # Vérifier si toutes les réponses sont vides
        if all(not ans.strip() for ans in user_answers):
            logger.info("Toutes les réponses utilisateur sont vides")
            return 0, total_count, [{
                'blank_index': i,
                'user_answer': '',
                'correct_answer': correct_answers[i] if i < len(correct_answers) else '',
                'is_correct': False,
                'status': 'Réponse vide',
                'sentence_index': -1
            } for i in range(total_count)]
        
        # Si certaines réponses sont vides, considérer l'exercice comme incorrect
        if any(not ans.strip() for ans in user_answers):
            logger.info("Certaines réponses utilisateur sont vides")
            return 0, total_count, [{
                'blank_index': i,
                'user_answer': user_answers[i] if i < len(user_answers) else '',
                'correct_answer': correct_answers[i] if i < len(correct_answers) else '',
                'is_correct': False,
                'status': 'Réponse incomplète',
                'sentence_index': -1
            } for i in range(total_count)]
            
        # Filtrer les réponses vides (ne devrait plus être nécessaire après les vérifications ci-dessus)
        user_answers_filtered = [ans for ans in user_answers if ans.strip()]
        correct_answers_filtered = [ans for ans in correct_answers if ans.strip()]
        
        logger.info(f"Réponses utilisateur filtrées: {user_answers_filtered}")
        logger.info(f"Réponses correctes filtrées: {correct_answers_filtered}")
        
        # Convertir en nombres flottants
        try:
            user_numbers = [float(ans) for ans in user_answers_filtered]
            correct_numbers = [float(ans) for ans in correct_answers_filtered]
        except ValueError:
            # Si la conversion en nombres échoue, essayer de comparer les chaînes directement
            user_numbers = user_answers_filtered
            correct_numbers = correct_answers_filtered
            logger.warning("Conversion en nombres impossible, comparaison de chaînes")
        
        logger.info(f"Nombres utilisateur: {user_numbers}")
        logger.info(f"Nombres corrects: {correct_numbers}")
        
        # Vérifier si les nombres sont dans le bon ordre
        is_correct_order = False
        
        if isinstance(user_numbers[0], float):
            # Comparaison numérique
            if ordering_type == 'croissant':
                is_correct_order = all(user_numbers[i] <= user_numbers[i+1] for i in range(len(user_numbers)-1))
            else:  # decroissant
                is_correct_order = all(user_numbers[i] >= user_numbers[i+1] for i in range(len(user_numbers)-1))
        else:
            # Comparaison alphabétique
            if ordering_type == 'croissant':
                is_correct_order = all(user_numbers[i] <= user_numbers[i+1] for i in range(len(user_numbers)-1))
            else:  # decroissant
                is_correct_order = all(user_numbers[i] >= user_numbers[i+1] for i in range(len(user_numbers)-1))
        
        logger.info(f"Ordre correct: {is_correct_order}")
        
        # Vérifier si tous les nombres attendus sont présents
        all_numbers_present = set(str(n) for n in user_numbers) == set(str(n) for n in correct_numbers)
        logger.info(f"Tous les nombres présents: {all_numbers_present}")
        
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
            
    except Exception as e:
        # En cas d'erreur, retourner 0 correct
        logger.error(f"Erreur lors de l'évaluation: {e}")
        correct_count = 0
        
    return correct_count, total_count, feedback_details

def patch_app_for_ordering_exercises():
    """
    Génère le code à insérer dans app.py pour corriger le scoring des exercices de rangement
    """
    patch_code = """
# Début du patch pour les exercices de type "ranger par ordre"
from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise

# Dans la section de traitement des exercices fill_in_blanks, ajouter:
# Après avoir récupéré les réponses correctes et calculé total_blanks

# Détecter si c'est un exercice de type "ranger par ordre"
is_ordering, ordering_type = is_ordering_exercise(exercise.description)

if is_ordering and ordering_type:
    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Détecté exercice de rangement par ordre {ordering_type}")
    
    # Récupérer toutes les réponses de l'utilisateur
    user_answers_list = []
    for i in range(total_blanks):
        user_answer = request.form.get(f'answer_{i}', '').strip()
        user_answers_list.append(user_answer)
        user_answers_data[f'answer_{i}'] = user_answer
    
    # Utiliser notre fonction spécialisée pour évaluer l'exercice de rangement
    correct_blanks, _, feedback_details = evaluate_ordering_exercise(
        user_answers_list, correct_answers, ordering_type
    )
else:
    # Continuer avec la logique standard pour les exercices fill_in_blanks normaux
    # ...
# Fin du patch
"""
    return patch_code

# Test du script
if __name__ == "__main__":
    # Test de détection
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
    
    # Test d'évaluation
    user_answers = ["0.08", "0.18", "0.8", "0.85", "0.9"]  # Ordre croissant correct
    correct_answers = ["0.9", "0.85", "0.08", "0.8", "0.18"]  # Désordre
    
    correct_count, total_count, feedback = evaluate_ordering_exercise(
        user_answers, correct_answers, 'croissant'
    )
    
    print(f"\nTest d'évaluation:")
    print(f"  - Score: {correct_count}/{total_count} ({(correct_count/total_count)*100}%)")
    print(f"  - Feedback: {json.dumps(feedback, indent=2)}")
