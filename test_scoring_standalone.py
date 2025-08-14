#!/usr/bin/env python3
"""
Test autonome de la logique de scoring pour les textes à trous
"""

def test_scoring_logic():
    """Test de la logique de scoring pour fill_in_blanks"""
    print("=== TEST SCORING FILL_IN_BLANKS ===")
    
    # Exemple d'exercice avec plusieurs blancs dans une phrase
    content = {
        "sentences": [
            "Le ___ mange une ___ rouge dans le ___.",
            "La ___ vole vers son ___."
        ],
        "words": ["chat", "pomme", "jardin", "oiseau", "nid"]
    }
    
    # Compter le nombre réel de blancs
    total_blanks_in_content = 0
    
    if 'text' in content:
        text_blanks = content['text'].count('___')
        total_blanks_in_content += text_blanks
        print(f"Format 'text' detected: {text_blanks} blanks in text")
    
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        total_blanks_in_content += sentences_blanks
        print(f"Format 'sentences' detected: {sentences_blanks} blanks in sentences")
    
    print(f"Total blanks found in content: {total_blanks_in_content}")
    
    # Récupérer les réponses correctes
    correct_answers = content.get('words', [])
    if not correct_answers:
        correct_answers = content.get('available_words', [])
    
    print(f"Found {len(correct_answers)} correct answers: {correct_answers}")
    
    # Utiliser le nombre réel de blancs trouvés dans le contenu
    total_blanks = max(total_blanks_in_content, len(correct_answers))
    print(f"Using total_blanks = {total_blanks}")
    
    # Test 1: Toutes les réponses correctes
    print("\n=== TEST 1: TOUTES RÉPONSES CORRECTES ===")
    user_answers = {
        'answer_0': 'chat',      # Correct
        'answer_1': 'pomme',     # Correct  
        'answer_2': 'jardin',    # Correct
        'answer_3': 'oiseau',    # Correct
        'answer_4': 'nid'        # Correct
    }
    
    correct_blanks = 0
    for i in range(total_blanks):
        user_answer = user_answers.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        # Logique word_placement
        is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
        if is_correct:
            correct_blanks += 1
        
        print(f"Blanc {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    # Calculer le score final avec la logique word_placement
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    
    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"Score: {correct_blanks}/{total_blanks} = {score}%")
    
    # Test 2: Réponses partielles
    print("\n=== TEST 2: RÉPONSES PARTIELLES ===")
    user_answers_partial = {
        'answer_0': 'chat',      # Correct
        'answer_1': 'banane',    # Incorrect
        'answer_2': 'jardin',    # Correct
        'answer_3': 'aigle',     # Incorrect
        'answer_4': 'nid'        # Correct
    }
    
    correct_blanks_partial = 0
    for i in range(total_blanks):
        user_answer = user_answers_partial.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        # Logique word_placement
        is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
        if is_correct:
            correct_blanks_partial += 1
        
        print(f"Blanc {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    # Calculer le score final avec la logique word_placement
    score_partial = (correct_blanks_partial / total_blanks) * 100 if total_blanks > 0 else 0
    
    print(f"\n=== RÉSULTAT FINAL PARTIEL ===")
    print(f"Score: {correct_blanks_partial}/{total_blanks} = {score_partial}%")
    
    # Test 3: Réponse vide
    print("\n=== TEST 3: RÉPONSE VIDE ===")
    user_answers_empty = {
        'answer_0': '',          # Vide
        'answer_1': '',          # Vide
        'answer_2': '',          # Vide
        'answer_3': '',          # Vide
        'answer_4': ''           # Vide
    }
    
    correct_blanks_empty = 0
    for i in range(total_blanks):
        user_answer = user_answers_empty.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        # Logique word_placement
        is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
        if is_correct:
            correct_blanks_empty += 1
        
        print(f"Blanc {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    # Calculer le score final avec la logique word_placement
    score_empty = (correct_blanks_empty / total_blanks) * 100 if total_blanks > 0 else 0
    
    print(f"\n=== RÉSULTAT FINAL VIDE ===")
    print(f"Score: {correct_blanks_empty}/{total_blanks} = {score_empty}%")

if __name__ == '__main__':
    test_scoring_logic()
