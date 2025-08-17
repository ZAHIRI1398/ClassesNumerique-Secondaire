"""
Script de test pour vérifier la correction du problème de scoring des exercices fill_in_blanks
avec plusieurs blancs sur la même ligne.
"""

from get_blank_location import get_blank_location

def test_get_blank_location():
    """Teste la fonction get_blank_location avec différents scénarios"""
    print("Test de la fonction get_blank_location")
    
    # Cas 1: Phrases simples avec un blanc par phrase
    sentences1 = ["Le ___ est bleu", "La ___ est rouge", "Le ___ est vert"]
    print("\nCas 1: Un blanc par phrase")
    for i in range(3):
        sentence_idx, local_idx = get_blank_location(i, sentences1)
        print(f"Blank global {i} -> Phrase {sentence_idx}, Position locale {local_idx}")
    
    # Cas 2: Phrase avec plusieurs blancs
    sentences2 = ["Le ___ mange une ___ rouge", "La ___ est belle"]
    print("\nCas 2: Plusieurs blancs dans une phrase")
    for i in range(3):
        sentence_idx, local_idx = get_blank_location(i, sentences2)
        print(f"Blank global {i} -> Phrase {sentence_idx}, Position locale {local_idx}")
    
    # Cas 3: Mélange complexe
    sentences3 = ["Le ___ ___ une pomme", "La ___ est ___ et ___", "Le ___ dort"]
    print("\nCas 3: Mélange complexe")
    for i in range(6):
        sentence_idx, local_idx = get_blank_location(i, sentences3)
        print(f"Blank global {i} -> Phrase {sentence_idx}, Position locale {local_idx}")

def test_scoring_simulation():
    """Simule le scoring d'un exercice fill_in_blanks avec plusieurs blancs par ligne"""
    print("\nTest de simulation de scoring")
    
    # Contenu de l'exercice
    content = {
        "sentences": ["Le ___ mange une ___ rouge", "La ___ est belle"],
        "words": ["chat", "pomme", "maison"]
    }
    
    # Simuler des réponses utilisateur
    user_answers = {
        'answer_0': 'chat',
        'answer_1': 'pomme',
        'answer_2': 'maison'
    }
    
    # Compter les blancs
    total_blanks = sum(s.count('___') for s in content['sentences'])
    print(f"Total des blancs: {total_blanks}")
    
    # Vérifier les réponses
    correct_blanks = 0
    for i in range(total_blanks):
        # Récupérer la réponse de l'utilisateur
        user_answer = user_answers.get(f'answer_{i}', '').strip()
        
        # Récupérer la réponse correcte
        correct_answer = content['words'][i] if i < len(content['words']) else ''
        
        # Déterminer l'emplacement du blanc
        sentence_idx, local_blank_idx = get_blank_location(i, content['sentences'])
        
        # Vérifier si la réponse est correcte
        is_correct = user_answer.lower() == correct_answer.lower()
        if is_correct:
            correct_blanks += 1
        
        print(f"Blank {i} (phrase {sentence_idx}, pos {local_blank_idx}):")
        print(f"  - Réponse utilisateur: {user_answer}")
        print(f"  - Réponse correcte: {correct_answer}")
        print(f"  - Correct: {is_correct}")
    
    # Calculer le score
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    print(f"\nScore final: {score}% ({correct_blanks}/{total_blanks})")

if __name__ == "__main__":
    print("=== TEST DE LA CORRECTION POUR FILL_IN_BLANKS AVEC PLUSIEURS BLANCS PAR LIGNE ===\n")
    test_get_blank_location()
    test_scoring_simulation()
