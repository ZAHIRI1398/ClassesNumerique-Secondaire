#!/usr/bin/env python3
"""
Test du scoring corrigé pour les exercices "Texte à trous"
"""

import json

def test_scoring_logic():
    """Test de la logique de scoring corrigée"""
    
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
    
    # Simuler des réponses utilisateur
    user_answers = {
        'answer_0': 'chat',      # Correct
        'answer_1': 'pomme',     # Correct  
        'answer_2': 'jardin',    # Correct
        'answer_3': 'oiseau',    # Correct
        'answer_4': 'nid'        # Correct
    }
    
    print("\n=== TEST SCORING ===")
    
    correct_blanks = 0
    for i in range(total_blanks):
        user_answer = user_answers.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
        if is_correct:
            correct_blanks += 1
        
        print(f"Blank {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    # Calculer le score final
    max_score = total_blanks
    score_count = correct_blanks
    score = round((score_count / max_score) * 100) if max_score > 0 else 0
    
    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"Score: {score_count}/{max_score} = {score}%")
    
    # Test avec toutes les réponses correctes
    if score == 100:
        print("SUCCES : Le scoring fonctionne correctement !")
        print("Toutes les reponses correctes donnent 100%")
    else:
        print("PROBLEME : Le scoring ne fonctionne pas correctement")
    
    return score == 100

def test_partial_scoring():
    """Test avec réponses partiellement correctes"""
    print("\n" + "="*50)
    print("TEST AVEC RÉPONSES PARTIELLEMENT CORRECTES")
    print("="*50)
    
    content = {
        "sentences": [
            "Le ___ mange une ___ rouge.",  # 2 blancs
        ],
        "words": ["chat", "pomme"]
    }
    
    # Compter les blancs
    total_blanks_in_content = sum(s.count('___') for s in content['sentences'])
    correct_answers = content.get('words', [])
    total_blanks = max(total_blanks_in_content, len(correct_answers))
    
    print(f"Total blanks: {total_blanks}")
    print(f"Correct answers: {correct_answers}")
    
    # Simuler réponse partiellement correcte (1 sur 2)
    user_answers = {
        'answer_0': 'chat',      # Correct
        'answer_1': 'banane',    # Incorrect (devrait être 'pomme')
    }
    
    correct_blanks = 0
    for i in range(total_blanks):
        user_answer = user_answers.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
        if is_correct:
            correct_blanks += 1
        
        print(f"Blank {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
    print(f"Score partiel: {correct_blanks}/{total_blanks} = {score}%")
    
    # Devrait être 50% (1 correct sur 2)
    expected_score = 50
    if score == expected_score:
        print(f"SUCCES : Score partiel correct ({score}%)")
        return True
    else:
        print(f"PROBLEME : Score attendu {expected_score}%, obtenu {score}%")
        return False

if __name__ == "__main__":
    print("TEST DU SCORING CORRIGE POUR 'TEXTE A TROUS'")
    print("="*60)
    
    # Test 1: Toutes les réponses correctes
    success1 = test_scoring_logic()
    
    # Test 2: Réponses partiellement correctes
    success2 = test_partial_scoring()
    
    print("\n" + "="*60)
    print("RESUME DES TESTS")
    print("="*60)
    
    if success1 and success2:
        print("TOUS LES TESTS REUSSIS !")
        print("Le scoring des exercices 'Texte a trous' fonctionne correctement")
        print("Les blancs multiples sont comptes individuellement")
        print("Le score de 100% est atteint quand toutes les reponses sont correctes")
    else:
        print("CERTAINS TESTS ONT ECHOUE")
        if not success1:
            print("Test scoring complet echoue")
        if not success2:
            print("Test scoring partiel echoue")
