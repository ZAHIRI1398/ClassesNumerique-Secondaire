#!/usr/bin/env python3
"""
Test complet pour verifier le bon fonctionnement du scoring des exercices "texte a trous"
avec plusieurs blancs dans une ligne.

Ce script teste plusieurs scenarios:
1. Exercice avec plusieurs blancs dans une meme phrase
2. Exercice avec blancs repartis sur plusieurs phrases
3. Exercice avec mots repetes
4. Exercice avec format 'text' au lieu de 'sentences'
5. Exercice avec melange de 'text' et 'sentences'
"""

import json
import sys
from datetime import datetime

class TestResult:
    """Classe pour stocker les resultats des tests"""
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = []
    
    def add_result(self, test_name, passed, message=""):
        """Ajoute un resultat de test"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"[SUCCES] {test_name}: REUSSI")
        else:
            self.failed_tests.append((test_name, message))
            print(f"[ECHEC] {test_name}: ECHOUE - {message}")
    
    def summary(self):
        """Affiche un resume des tests"""
        print("\n" + "="*60)
        print(f"RESUME DES TESTS: {self.passed_tests}/{self.total_tests} reussis")
        print("="*60)
        
        if self.failed_tests:
            print("\nTests echoues:")
            for name, message in self.failed_tests:
                print(f"- {name}: {message}")
            return False
        else:
            print("\nTous les tests ont reussi!")
            return True

def test_scoring(content, user_answers, expected_score, test_name):
    """
    Teste le scoring d'un exercice avec les reponses donnees.
    
    Args:
        content: Contenu de l'exercice (dict)
        user_answers: Reponses de l'utilisateur (dict)
        expected_score: Score attendu (float)
        test_name: Nom du test (str)
        
    Returns:
        bool: True si le test a reussi, False sinon
    """
    print("\n" + "-"*60)
    print(f"TEST: {test_name}")
    print("-"*60)
    
    # Compter le nombre de blancs dans le contenu
    total_blanks_in_content = 0
    
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
    
    print(f"Réponses correctes ({len(correct_answers)}): {correct_answers}")
    
    # Utiliser le nombre réel de blancs trouvés dans le contenu
    total_blanks = max(total_blanks_in_content, len(correct_answers))
    print(f"Total blancs utilisé pour scoring: {total_blanks}")
    
    # Vérifier chaque réponse
    correct_blanks = 0
    for i in range(total_blanks):
        user_answer = user_answers.get(f'answer_{i}', '').strip()
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
        if is_correct:
            correct_blanks += 1
        
        print(f"Blank {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
    
    # Calculer le score
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    
    print(f"\nScore calcule: {score:.1f}% ({correct_blanks}/{total_blanks})")
    print(f"Score attendu: {expected_score:.1f}%")
    
    # Verifier si le score correspond a l'attendu
    is_success = abs(score - expected_score) < 0.1  # Tolerance de 0.1%
    
    if is_success:
        print(f"[SUCCES] Test reussi: Le score calcule correspond au score attendu")
    else:
        print(f"[ECHEC] Test echoue: Le score calcule ({score:.1f}%) ne correspond pas au score attendu ({expected_score:.1f}%)")
    
    return is_success, f"Score calcule: {score:.1f}%, attendu: {expected_score:.1f}%"

def test_multiple_blanks_in_one_sentence():
    """Test avec plusieurs blancs dans une meme phrase"""
    content = {
        "sentences": [
            "Le ___ mange une ___ rouge dans le ___.",  # 3 blancs dans 1 phrase
        ],
        "words": ["chat", "pomme", "jardin"]
    }
    
    # Toutes les reponses correctes
    user_answers_correct = {
        'answer_0': 'chat',
        'answer_1': 'pomme',
        'answer_2': 'jardin'
    }
    
    # Reponses partiellement correctes (2/3)
    user_answers_partial = {
        'answer_0': 'chat',
        'answer_1': 'banane',  # Incorrect
        'answer_2': 'jardin'
    }
    
    # Reponses incorrectes
    user_answers_incorrect = {
        'answer_0': 'chien',   # Incorrect
        'answer_1': 'banane',  # Incorrect
        'answer_2': 'maison'   # Incorrect
    }
    
    results = []
    results.append(test_scoring(content, user_answers_correct, 100.0, "Plusieurs blancs dans une phrase - Toutes correctes"))
    results.append(test_scoring(content, user_answers_partial, 66.7, "Plusieurs blancs dans une phrase - Partiellement correctes"))
    results.append(test_scoring(content, user_answers_incorrect, 0.0, "Plusieurs blancs dans une phrase - Toutes incorrectes"))
    
    return results

def test_blanks_across_multiple_sentences():
    """Test avec blancs repartis sur plusieurs phrases"""
    content = {
        "sentences": [
            "Le ___ est un animal.",        # 1 blanc
            "La ___ est un fruit.",         # 1 blanc
            "Le ___ et la ___ sont ici."    # 2 blancs
        ],
        "words": ["chat", "pomme", "chien", "banane"]
    }
    
    # Toutes les reponses correctes
    user_answers_correct = {
        'answer_0': 'chat',
        'answer_1': 'pomme',
        'answer_2': 'chien',
        'answer_3': 'banane'
    }
    
    # Reponses partiellement correctes (2/4)
    user_answers_partial = {
        'answer_0': 'chat',
        'answer_1': 'pomme',
        'answer_2': 'oiseau',  # Incorrect
        'answer_3': 'orange'   # Incorrect
    }
    
    results = []
    results.append(test_scoring(content, user_answers_correct, 100.0, "Blancs sur plusieurs phrases - Toutes correctes"))
    results.append(test_scoring(content, user_answers_partial, 50.0, "Blancs sur plusieurs phrases - Partiellement correctes"))
    
    return results

def test_repeated_words():
    """Test avec mots repetes"""
    content = {
        "sentences": [
            "Le ___ est un animal. Le ___ est carnivore.",  # 2 fois "chat"
            "La ___ est rouge. J'aime les ___."            # 2 fois "pomme"
        ],
        "words": ["chat", "chat", "pomme", "pomme"]
    }
    
    # Toutes les reponses correctes
    user_answers_correct = {
        'answer_0': 'chat',
        'answer_1': 'chat',
        'answer_2': 'pomme',
        'answer_3': 'pomme'
    }
    
    # Reponses partiellement correctes (3/4)
    user_answers_partial = {
        'answer_0': 'chat',
        'answer_1': 'chat',
        'answer_2': 'pomme',
        'answer_3': 'orange'  # Incorrect
    }
    
    results = []
    results.append(test_scoring(content, user_answers_correct, 100.0, "Mots repetes - Toutes correctes"))
    results.append(test_scoring(content, user_answers_partial, 75.0, "Mots repetes - Partiellement correctes"))
    
    return results

def test_text_format():
    """Test avec format 'text' au lieu de 'sentences'"""
    content = {
        "text": "Le ___ mange une ___. La ___ est ___.",  # 4 blancs
        "words": ["chat", "pomme", "maison", "grande"]
    }
    
    # Toutes les reponses correctes
    user_answers_correct = {
        'answer_0': 'chat',
        'answer_1': 'pomme',
        'answer_2': 'maison',
        'answer_3': 'grande'
    }
    
    # Reponses partiellement correctes (2/4)
    user_answers_partial = {
        'answer_0': 'chat',
        'answer_1': 'banane',  # Incorrect
        'answer_2': 'maison',
        'answer_3': 'petit'    # Incorrect
    }
    
    results = []
    results.append(test_scoring(content, user_answers_correct, 100.0, "Format 'text' - Toutes correctes"))
    results.append(test_scoring(content, user_answers_partial, 50.0, "Format 'text' - Partiellement correctes"))
    
    return results

def test_mixed_format():
    """Test avec melange de 'text' et 'sentences' (priorite a 'sentences')"""
    content = {
        "text": "Ceci est un texte avec des ___ qui ne devraient pas etre comptes.",  # 1 blanc (ignoré)
        "sentences": [
            "Le ___ mange une ___.",  # 2 blancs (comptés)
        ],
        "words": ["chat", "pomme"]
    }
    
    # Toutes les reponses correctes
    user_answers_correct = {
        'answer_0': 'chat',
        'answer_1': 'pomme'
    }
    
    # Reponses incorrectes
    user_answers_incorrect = {
        'answer_0': 'chien',   # Incorrect
        'answer_1': 'banane'   # Incorrect
    }
    
    results = []
    results.append(test_scoring(content, user_answers_correct, 100.0, "Format mixte - Toutes correctes"))
    results.append(test_scoring(content, user_answers_incorrect, 0.0, "Format mixte - Toutes incorrectes"))
    
    return results

def test_edge_cases():
    """Test des cas limites"""
    
    # Cas 1: Aucun blanc mais des mots
    content1 = {
        "sentences": [
            "Cette phrase n'a pas de blancs.",
        ],
        "words": ["mot1", "mot2"]
    }
    
    # Cas 2: Des blancs mais aucun mot
    content2 = {
        "sentences": [
            "Cette phrase a des ___ mais pas de mots.",
        ],
        "words": []
    }
    
    # Cas 3: Nombre de blancs différent du nombre de mots
    content3 = {
        "sentences": [
            "Cette phrase a ___ blancs.",  # 1 blanc
        ],
        "words": ["deux", "mots"]  # 2 mots
    }
    
    results = []
    results.append(test_scoring(content1, {'answer_0': 'mot1', 'answer_1': 'mot2'}, 100.0, "Cas limite - Aucun blanc mais des mots"))
    results.append(test_scoring(content2, {}, 0.0, "Cas limite - Des blancs mais aucun mot"))
    results.append(test_scoring(content3, {'answer_0': 'deux'}, 50.0, "Cas limite - Nombre de blancs != nombre de mots"))
    
    return results

def run_all_tests():
    """Execute tous les tests et affiche un resume"""
    print("="*60)
    print("TEST COMPLET DU SCORING DES EXERCICES 'TEXTE A TROUS'")
    print("="*60)
    print(f"Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    test_result = TestResult()
    
    # Exécuter tous les tests
    all_test_results = []
    all_test_results.extend(test_multiple_blanks_in_one_sentence())
    all_test_results.extend(test_blanks_across_multiple_sentences())
    all_test_results.extend(test_repeated_words())
    all_test_results.extend(test_text_format())
    all_test_results.extend(test_mixed_format())
    all_test_results.extend(test_edge_cases())
    
    # Ajouter les résultats
    for i, (result, message) in enumerate(all_test_results):
        test_name = f"Test {i+1}"
        test_result.add_result(test_name, result, message)
    
    # Afficher le résumé
    success = test_result.summary()
    
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
