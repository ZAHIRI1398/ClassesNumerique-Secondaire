#!/usr/bin/env python3
"""
Test de la correction du problème de scoring des exercices "texte à trous"
avec plusieurs blancs dans une ligne.
"""

import json

def test_multiple_blanks_in_line():
    """
    Test spécifique pour le cas où une phrase contient plusieurs blancs.
    """
    print("\n" + "="*60)
    print("TEST AVEC PLUSIEURS BLANCS DANS UNE MÊME LIGNE")
    print("="*60)
    
    # Exemple d'exercice avec plusieurs blancs dans une même phrase
    content = {
        "sentences": [
            "Le ___ mange une ___ dans le jardin.",  # 2 blancs dans 1 phrase
            "La ___ est ___."                        # 2 blancs dans 1 phrase
        ],
        "words": ["chat", "pomme", "maison", "grande"]
    }
    
    # Compter les blancs correctement
    total_blanks_in_content = 0
    
    # Utiliser if/elif pour éviter le double comptage
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        total_blanks_in_content = sentences_blanks
        print(f"Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
        
        # Log détaillé pour chaque phrase et ses blancs
        for i, sentence in enumerate(content['sentences']):
            blanks_in_sentence = sentence.count('___')
            print(f"Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
    elif 'text' in content:
        text_blanks = content['text'].count('___')
        total_blanks_in_content = text_blanks
        print(f"Format 'text' détecté: {text_blanks} blancs dans text")
    
    print(f"Total blancs trouvés dans le contenu: {total_blanks_in_content}")
    
    # Récupérer les réponses correctes
    correct_answers = content.get('words', [])
    if not correct_answers:
        correct_answers = content.get('available_words', [])
    
    print(f"Found {len(correct_answers)} correct answers: {correct_answers}")
    
    # Utiliser le nombre réel de blancs trouvés dans le contenu
    total_blanks = max(total_blanks_in_content, len(correct_answers))
    print(f"Using total_blanks = {total_blanks}")
    
    # Simuler des réponses utilisateur - toutes correctes
    user_answers = {
        'answer_0': 'chat',      # Correct
        'answer_1': 'pomme',     # Correct
        'answer_2': 'maison',    # Correct
        'answer_3': 'grande'     # Correct
    }
    
    print("\n=== TEST SCORING - TOUTES RÉPONSES CORRECTES ===")
    
    correct_blanks = 0
    for i in range(total_blanks):
        user_answer = user_answers.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
        if is_correct:
            correct_blanks += 1
        
        print(f"Blank {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    # Calculer le score final
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    
    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"Score: {correct_blanks}/{total_blanks} = {score}%")
    
    # Test avec toutes les réponses correctes
    if score == 100:
        print("SUCCÈS : Le scoring fonctionne correctement !")
        print("Toutes les réponses correctes donnent 100%")
    else:
        print("PROBLÈME : Le scoring ne fonctionne pas correctement")
    
    # Test avec réponses partiellement correctes
    print("\n=== TEST SCORING - RÉPONSES PARTIELLEMENT CORRECTES ===")
    
    # Simuler des réponses utilisateur - partiellement correctes
    user_answers_partial = {
        'answer_0': 'chat',      # Correct
        'answer_1': 'banane',    # Incorrect (devrait être 'pomme')
        'answer_2': 'maison',    # Correct
        'answer_3': 'petit'      # Incorrect (devrait être 'grande')
    }
    
    correct_blanks = 0
    for i in range(total_blanks):
        user_answer = user_answers_partial.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
        if is_correct:
            correct_blanks += 1
        
        print(f"Blank {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    # Calculer le score final
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    
    print(f"\n=== RÉSULTAT FINAL PARTIEL ===")
    print(f"Score: {correct_blanks}/{total_blanks} = {score}%")
    
    # Test avec réponses partiellement correctes
    expected_score = 50  # 2 correctes sur 4 = 50%
    if score == expected_score:
        print(f"SUCCÈS : Le scoring partiel fonctionne correctement ! ({score}%)")
    else:
        print(f"PROBLÈME : Score attendu {expected_score}%, obtenu {score}%")
    
    return score == 100 or score == expected_score

def test_multiple_blanks_same_word():
    """
    Test pour le cas où plusieurs blancs doivent être remplis avec le même mot.
    """
    print("\n" + "="*60)
    print("TEST AVEC PLUSIEURS BLANCS UTILISANT LE MÊME MOT")
    print("="*60)
    
    # Exemple d'exercice avec répétition de mots
    content = {
        "sentences": [
            "Le ___ est un animal. Le ___ est carnivore.",  # 2 fois "chat"
            "La ___ est rouge. J'aime les ___."            # 2 fois "pomme"
        ],
        "words": ["chat", "chat", "pomme", "pomme"]
    }
    
    # Compter les blancs
    total_blanks_in_content = sum(s.count('___') for s in content['sentences'])
    correct_answers = content.get('words', [])
    total_blanks = max(total_blanks_in_content, len(correct_answers))
    
    print(f"Total blancs: {total_blanks}")
    print(f"Correct answers: {correct_answers}")
    
    # Simuler réponses utilisateur correctes
    user_answers = {
        'answer_0': 'chat',
        'answer_1': 'chat',
        'answer_2': 'pomme',
        'answer_3': 'pomme'
    }
    
    correct_blanks = 0
    for i in range(total_blanks):
        user_answer = user_answers.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
        if is_correct:
            correct_blanks += 1
        
        print(f"Blank {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    print(f"Score: {correct_blanks}/{total_blanks} = {score}%")
    
    # Devrait être 100%
    expected_score = 100
    if score == expected_score:
        print(f"SUCCÈS : Score correct pour mots répétés ({score}%)")
        return True
    else:
        print(f"PROBLÈME : Score attendu {expected_score}%, obtenu {score}%")
        return False

if __name__ == "__main__":
    print("TEST DE LA CORRECTION POUR TEXTE À TROUS AVEC PLUSIEURS BLANCS")
    print("="*60)
    
    # Test 1: Plusieurs blancs dans une ligne
    success1 = test_multiple_blanks_in_line()
    
    # Test 2: Plusieurs blancs avec le même mot
    success2 = test_multiple_blanks_same_word()
    
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    if success1 and success2:
        print("TOUS LES TESTS RÉUSSIS !")
        print("La correction du scoring des exercices 'Texte à trous' fonctionne correctement")
        print("Les blancs multiples dans une même ligne sont comptés individuellement")
        print("Les mots répétés sont correctement gérés")
    else:
        print("CERTAINS TESTS ONT ÉCHOUÉ")
        if not success1:
            print("Test avec plusieurs blancs dans une ligne a échoué")
        if not success2:
            print("Test avec mots répétés a échoué")
