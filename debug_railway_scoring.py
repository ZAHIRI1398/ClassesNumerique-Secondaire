#!/usr/bin/env python3
"""
Script de diagnostic pour Railway - Vérifie la logique de scoring des textes à trous
"""

import os
import sys
import json
import datetime
import platform

# Ajouter le répertoire courant au path pour les imports
sys.path.append('.')

# Fonction pour tester la logique de scoring
def test_fill_in_blanks_scoring(content, user_answers):
    """
    Teste la logique de scoring pour un exercice fill_in_blanks
    
    Args:
        content: Contenu JSON de l'exercice
        user_answers: Dictionnaire des réponses utilisateur (answer_0, answer_1, etc.)
        
    Returns:
        dict: Résultats du test avec score et détails
    """
    results = {
        "success": True,
        "score": 0,
        "correct_count": 0,
        "total_blanks": 0,
        "details": [],
        "error": None
    }
    
    try:
        # Logique de comptage des blancs
        total_blanks_in_content = 0
        
        if 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content += text_blanks
            results["details"].append(f"Format 'text' détecté: {text_blanks} blancs")
        
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content += sentences_blanks
            results["details"].append(f"Format 'sentences' détecté: {sentences_blanks} blancs")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        results["details"].append(f"Trouvé {len(correct_answers)} réponses correctes: {correct_answers}")
        
        # Utiliser le nombre réel de blancs trouvés dans le contenu
        total_blanks = max(total_blanks_in_content, len(correct_answers))
        results["total_blanks"] = total_blanks
        
        # Vérifier chaque réponse
        correct_blanks = 0
        blank_details = []
        
        for i in range(total_blanks):
            user_answer = user_answers.get(f'answer_{i}', '').strip()
            correct_answer = correct_answers[i] if i < len(correct_answers) else ''
            
            # Logique word_placement
            is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
            if is_correct:
                correct_blanks += 1
            
            blank_details.append({
                "blank_index": i,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })
        
        results["correct_count"] = correct_blanks
        results["blank_details"] = blank_details
        
        # Calculer le score final avec la logique word_placement
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        results["score"] = score
        
    except Exception as e:
        results["success"] = False
        results["error"] = str(e)
    
    return results

# Fonction pour obtenir les informations système
def get_system_info():
    """Récupère les informations système"""
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "date": datetime.datetime.now().isoformat(),
        "env_vars": {k: v for k, v in os.environ.items() if k in ['FLASK_ENV', 'FLASK_DEBUG', 'DATABASE_URL', 'RAILWAY_ENVIRONMENT']}
    }
    return info

# Fonction principale
def main():
    """Fonction principale du diagnostic"""
    results = {
        "system_info": get_system_info(),
        "tests": {}
    }
    
    # Test 1: Exemple simple avec toutes les réponses correctes
    content_simple = {
        "sentences": ["Le ___ mange une ___ rouge."],
        "words": ["chat", "pomme"]
    }
    
    user_answers_all_correct = {
        'answer_0': 'chat',
        'answer_1': 'pomme'
    }
    
    results["tests"]["test_simple_all_correct"] = test_fill_in_blanks_scoring(
        content_simple, 
        user_answers_all_correct
    )
    
    # Test 2: Exemple simple avec réponses partielles
    user_answers_partial = {
        'answer_0': 'chat',
        'answer_1': 'banane'  # Incorrect
    }
    
    results["tests"]["test_simple_partial"] = test_fill_in_blanks_scoring(
        content_simple, 
        user_answers_partial
    )
    
    # Test 3: Exemple complexe
    content_complex = {
        "sentences": [
            "Le ___ mange une ___ rouge dans le ___.",
            "La ___ vole vers son ___."
        ],
        "words": ["chat", "pomme", "jardin", "oiseau", "nid"]
    }
    
    user_answers_complex = {
        'answer_0': 'chat',
        'answer_1': 'pomme',
        'answer_2': 'jardin',
        'answer_3': 'oiseau',
        'answer_4': 'nid'
    }
    
    results["tests"]["test_complex"] = test_fill_in_blanks_scoring(
        content_complex, 
        user_answers_complex
    )
    
    # Test 4: Format texte
    content_text = {
        "text": "Le ___ est un animal de compagnie. La ___ est un fruit.",
        "available_words": ["chat", "pomme"]
    }
    
    user_answers_text = {
        'answer_0': 'chat',
        'answer_1': 'pomme'
    }
    
    results["tests"]["test_text_format"] = test_fill_in_blanks_scoring(
        content_text, 
        user_answers_text
    )
    
    # Afficher les résultats
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Vérifier si tous les tests ont réussi
    all_success = all(test["success"] for test in results["tests"].values())
    all_scores_correct = all(
        (test["correct_count"] == test["total_blanks"]) 
        for test_name, test in results["tests"].items() 
        if test_name.endswith("_all_correct") or test_name == "test_complex" or test_name == "test_text_format"
    )
    
    if all_success and all_scores_correct:
        print("\n[OK] DIAGNOSTIC: Tous les tests ont réussi!")
        return 0
    else:
        print("\n[ERREUR] DIAGNOSTIC: Certains tests ont échoué!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
