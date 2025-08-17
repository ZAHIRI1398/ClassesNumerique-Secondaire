#!/usr/bin/env python3
"""
Script pour tester localement la logique de scoring des exercices fill_in_blanks et word_placement
Ce script simule la logique de scoring pour vérifier que la correction fonctionne correctement.
"""
import json
import re

def count_blanks_in_content(content):
    """
    Compte le nombre de blanks dans le contenu d'un exercice
    en utilisant la logique corrigée (priorité à sentences)
    """
    total_blanks = 0
    
    if 'sentences' in content:
        # Priorité aux phrases si elles existent
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        total_blanks = sentences_blanks
        print(f"[INFO] Comptage des blancs depuis 'sentences': {total_blanks} blancs trouvés")
    elif 'text' in content:
        # Sinon, utiliser le texte
        text_blanks = content['text'].count('___')
        total_blanks = text_blanks
        print(f"[INFO] Comptage des blancs depuis 'text': {total_blanks} blancs trouvés")
    else:
        print("[ERREUR] Aucun champ 'sentences' ou 'text' trouvé dans le contenu")
    
    return total_blanks

def get_correct_answers(content):
    """
    Récupère les réponses correctes depuis le contenu d'un exercice
    """
    correct_answers = []
    
    if 'words' in content:
        correct_answers = content['words']
        print(f"[INFO] Réponses correctes depuis 'words': {correct_answers}")
    elif 'available_words' in content:
        correct_answers = content['available_words']
        print(f"[INFO] Réponses correctes depuis 'available_words': {correct_answers}")
    else:
        print("[ERREUR] Aucun champ 'words' ou 'available_words' trouvé dans le contenu")
    
    return correct_answers

def calculate_score_fill_in_blanks(content, user_answers):
    """
    Calcule le score pour un exercice fill_in_blanks
    en utilisant la logique corrigée
    """
    print("\n=== Test de scoring pour fill_in_blanks ===")
    
    # Compter le nombre de blancs dans le contenu
    total_blanks = count_blanks_in_content(content)
    if total_blanks == 0:
        print("[ERREUR] Aucun blanc trouvé dans le contenu")
        return 0
    
    # Récupérer les réponses correctes
    correct_answers = get_correct_answers(content)
    if not correct_answers:
        print("[ERREUR] Aucune réponse correcte trouvée dans le contenu")
        return 0
    
    # Vérifier la cohérence entre le nombre de blancs et le nombre de réponses
    if len(correct_answers) != total_blanks:
        print(f"[AVERTISSEMENT] Incohérence: {total_blanks} blancs mais {len(correct_answers)} réponses")
    
    # Compter les réponses correctes
    correct_count = 0
    for i, answer in enumerate(user_answers):
        if i < len(correct_answers) and answer.lower() == correct_answers[i].lower():
            correct_count += 1
            print(f"[INFO] Réponse {i+1}: '{answer}' est correcte")
        elif i < len(correct_answers):
            print(f"[INFO] Réponse {i+1}: '{answer}' est incorrecte (attendu: '{correct_answers[i]}')")
    
    # Calculer le score
    score = (correct_count / total_blanks) * 100
    print(f"[RÉSULTAT] Score: {score:.2f}% ({correct_count}/{total_blanks} réponses correctes)")
    
    return score

def calculate_score_word_placement(content, user_answers):
    """
    Calcule le score pour un exercice word_placement
    en utilisant la logique corrigée
    """
    print("\n=== Test de scoring pour word_placement ===")
    
    # Compter le nombre de blancs dans le contenu
    total_blanks = count_blanks_in_content(content)
    if total_blanks == 0:
        print("[ERREUR] Aucun blanc trouvé dans le contenu")
        return 0
    
    # Récupérer les réponses correctes
    correct_answers = get_correct_answers(content)
    if not correct_answers:
        print("[ERREUR] Aucune réponse correcte trouvée dans le contenu")
        return 0
    
    # Vérifier la cohérence entre le nombre de blancs et le nombre de réponses
    if len(correct_answers) != total_blanks:
        print(f"[AVERTISSEMENT] Incohérence: {total_blanks} blancs mais {len(correct_answers)} réponses")
    
    # Compter les réponses correctes
    correct_count = 0
    for i, answer in enumerate(user_answers):
        if i < len(correct_answers) and answer.lower() == correct_answers[i].lower():
            correct_count += 1
            print(f"[INFO] Réponse {i+1}: '{answer}' est correcte")
        elif i < len(correct_answers):
            print(f"[INFO] Réponse {i+1}: '{answer}' est incorrecte (attendu: '{correct_answers[i]}')")
    
    # Calculer le score
    score = (correct_count / total_blanks) * 100
    print(f"[RÉSULTAT] Score: {score:.2f}% ({correct_count}/{total_blanks} réponses correctes)")
    
    return score

def test_coordonnees_exercise():
    """
    Teste spécifiquement l'exercice "Les coordonnées"
    """
    print("\n=== Test de l'exercice 'Les coordonnées' ===")
    
    # Contenu simulé de l'exercice "Les coordonnées"
    content = {
        "sentences": [
            "Le point A a pour coordonnées (___; ___).",
            "Le point B a pour coordonnées (___; ___).",
            "Le point C a pour coordonnées (___; ___)."
        ],
        "words": ["2", "3", "5", "1", "4", "6"]
    }
    
    # Test avec toutes les réponses correctes
    print("\n[TEST] Toutes les réponses correctes:")
    user_answers = ["2", "3", "5", "1", "4", "6"]
    calculate_score_fill_in_blanks(content, user_answers)
    
    # Test avec des réponses partiellement correctes
    print("\n[TEST] Réponses partiellement correctes:")
    user_answers = ["2", "3", "5", "1", "0", "0"]
    calculate_score_fill_in_blanks(content, user_answers)
    
    # Test avec des réponses incorrectes
    print("\n[TEST] Toutes les réponses incorrectes:")
    user_answers = ["0", "0", "0", "0", "0", "0"]
    calculate_score_fill_in_blanks(content, user_answers)

def test_double_counting_issue():
    """
    Teste spécifiquement le problème de double comptage
    """
    print("\n=== Test du problème de double comptage ===")
    
    # Contenu avec à la fois 'text' et 'sentences'
    content = {
        "text": "Le point A a pour coordonnées (___; ___). Le point B a pour coordonnées (___; ___).",
        "sentences": [
            "Le point A a pour coordonnées (___; ___).",
            "Le point B a pour coordonnées (___; ___)."
        ],
        "words": ["2", "3", "5", "1"]
    }
    
    # Test avec la logique corrigée (priorité à sentences)
    print("\n[TEST] Logique corrigée (priorité à sentences):")
    total_blanks = count_blanks_in_content(content)
    print(f"[RÉSULTAT] Nombre total de blancs: {total_blanks}")
    
    # Simuler l'ancien code (double comptage)
    old_total_blanks = 0
    if 'text' in content:
        text_blanks = content['text'].count('___')
        old_total_blanks += text_blanks
        print(f"[INFO] Ancien code - Blancs dans 'text': {text_blanks}")
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        old_total_blanks += sentences_blanks
        print(f"[INFO] Ancien code - Blancs dans 'sentences': {sentences_blanks}")
    
    print(f"[RÉSULTAT] Ancien code - Nombre total de blancs: {old_total_blanks}")
    print(f"[CONCLUSION] Différence: {old_total_blanks - total_blanks} blancs en trop avec l'ancien code")

def main():
    """Fonction principale"""
    print("=== Test de la logique de scoring des exercices fill_in_blanks et word_placement ===\n")
    
    # Tester l'exercice "Les coordonnées"
    test_coordonnees_exercise()
    
    # Tester le problème de double comptage
    test_double_counting_issue()
    
    print("\n=== Tests terminés ===")

if __name__ == "__main__":
    main()
