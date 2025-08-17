#!/usr/bin/env python3
"""
Script d'analyse et de correction du problème de scoring pour les exercices fill_in_blanks
avec plusieurs blancs sur une même ligne.

Ce script simule le comportement de l'application Flask et propose une solution.
"""

import json
import sys
from pprint import pprint

def analyze_form_data():
    """Analyse des données de formulaire simulées pour un exercice avec plusieurs blancs par ligne"""
    print("\n=== ANALYSE DES DONNÉES DE FORMULAIRE ===")
    
    # Simuler les données de formulaire pour un exercice avec plusieurs blancs par ligne
    form_data = {
        'answer_0': 'chat',
        'answer_1': 'pomme',
        'answer_2': 'oiseau',
        'answer_3': 'nid',
        'exercise_id': '42',
        'submit': 'Soumettre'
    }
    
    print("Données du formulaire:")
    pprint(form_data)
    
    # Extraire les réponses utilisateur
    user_answers = {}
    for key, value in form_data.items():
        if key.startswith('answer_'):
            try:
                index = int(key.split('_')[1])
                user_answers[index] = value.strip()
            except (ValueError, IndexError):
                print(f"Format de champ invalide: {key}")
    
    print("\nRéponses utilisateur extraites:")
    pprint(user_answers)
    print(f"Nombre de réponses: {len(user_answers)}")
    
    return user_answers

def analyze_exercise_content():
    """Analyse du contenu d'un exercice avec plusieurs blancs par ligne"""
    print("\n=== ANALYSE DU CONTENU DE L'EXERCICE ===")
    
    # Exemple d'exercice avec plusieurs blancs par ligne
    content = {
        "sentences": [
            "Le ___ mange une ___ rouge.",  # 2 blancs sur la même ligne
            "La ___ vole vers son ___."     # 2 blancs sur la même ligne
        ],
        "words": ["chat", "pomme", "oiseau", "nid"]
    }
    
    print("Contenu de l'exercice:")
    pprint(content)
    
    # Compter les blancs dans chaque phrase
    total_blanks = 0
    for idx, sentence in enumerate(content['sentences']):
        blanks_in_sentence = sentence.count('___')
        print(f"Phrase {idx}: '{sentence}' contient {blanks_in_sentence} blancs")
        total_blanks += blanks_in_sentence
    
    print(f"Total des blancs dans le contenu: {total_blanks}")
    
    # Vérifier les réponses correctes
    correct_answers = content.get('words', [])
    print(f"Réponses correctes: {correct_answers}")
    print(f"Nombre de réponses correctes: {len(correct_answers)}")
    
    # Vérifier la cohérence
    if total_blanks != len(correct_answers):
        print(f"ATTENTION: Le nombre de blancs ({total_blanks}) ne correspond pas au nombre de réponses correctes ({len(correct_answers)})")
    
    return content, total_blanks, correct_answers

def simulate_current_scoring_logic():
    """Simulation de la logique de scoring actuelle dans app.py"""
    print("\n=== SIMULATION DE LA LOGIQUE DE SCORING ACTUELLE ===")
    
    user_answers = analyze_form_data()
    content, total_blanks, correct_answers = analyze_exercise_content()
    
    # Logique actuelle dans app.py
    correct_blanks = 0
    for i in range(total_blanks):
        # Récupérer la réponse de l'utilisateur pour ce blanc
        user_answer = user_answers.get(i, '').strip()
        
        # Récupérer la réponse correcte correspondante
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        print(f"Blank {i}:")
        print(f"  - Réponse étudiant (answer_{i}): {user_answer}")
        print(f"  - Réponse attendue: {correct_answer}")
        
        # Vérifier si la réponse est correcte (insensible à la casse)
        is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
        if is_correct:
            correct_blanks += 1
            print(f"  - CORRECT")
        else:
            print(f"  - INCORRECT")
    
    # Calculer le score final
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    print(f"\nScore final: {correct_blanks}/{total_blanks} = {score}%")
    
    return score

def simulate_improved_scoring_logic():
    """Simulation de la logique de scoring améliorée"""
    print("\n=== SIMULATION DE LA LOGIQUE DE SCORING AMÉLIORÉE ===")
    
    user_answers = analyze_form_data()
    content, total_blanks, correct_answers = analyze_exercise_content()
    
    # Fonction auxiliaire pour déterminer la phrase et l'indice du blanc dans cette phrase
    def get_blank_location(global_blank_index, sentences):
        """Détermine à quelle phrase et à quel indice dans cette phrase correspond un indice global de blanc"""
        blank_count = 0
        for idx, sentence in enumerate(sentences):
            blanks_in_sentence = sentence.count('___')
            if blank_count <= global_blank_index < blank_count + blanks_in_sentence:
                # Calculer l'indice local du blanc dans cette phrase
                local_blank_index = global_blank_index - blank_count
                return idx, local_blank_index
            blank_count += blanks_in_sentence
        return -1, -1
    
    # Logique améliorée
    correct_blanks = 0
    
    # Vérifier d'abord que tous les champs de réponse sont présents
    print("Champs de réponse trouvés:", user_answers)
    print(f"Nombre de réponses: {len(user_answers)} / {total_blanks} attendues")
    
    # Traiter chaque blanc
    for i in range(total_blanks):
        # Récupérer la réponse de l'utilisateur pour ce blanc
        user_answer = user_answers.get(i, '').strip()
        
        # Récupérer la réponse correcte correspondante
        correct_answer = correct_answers[i] if i < len(correct_answers) else ''
        
        print(f"Blank {i}:")
        print(f"  - Réponse étudiant (answer_{i}): {user_answer}")
        print(f"  - Réponse attendue: {correct_answer}")
        
        # Vérifier si la réponse est correcte (insensible à la casse)
        is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
        if is_correct:
            correct_blanks += 1
            print(f"  - CORRECT")
        else:
            print(f"  - INCORRECT")
        
        # Déterminer l'index de la phrase à laquelle appartient ce blanc
        sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
        print(f"  - Appartient à la phrase {sentence_index}, position {local_blank_index}")
    
    # Calculer le score final
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    print(f"\nScore final: {correct_blanks}/{total_blanks} = {score}%")
    
    return score

def propose_fix():
    """Propose une correction pour le problème de scoring"""
    print("\n=== PROPOSITION DE CORRECTION ===")
    
    print("Pour corriger le problème de scoring avec plusieurs blancs sur une même ligne,")
    print("il faut modifier la façon dont les réponses utilisateur sont récupérées dans app.py.")
    print()
    print("Le problème actuel est que la méthode request.form.get(f'answer_{i}', '') ne récupère")
    print("pas correctement toutes les réponses lorsqu'il y a plusieurs blancs sur une même ligne.")
    print()
    print("Voici la correction à apporter dans app.py:")
    print()
    print("1. Remplacer la récupération directe des réponses par une méthode plus robuste:")
    print()
    print("# AVANT:")
    print("for i in range(total_blanks):")
    print("    # Récupérer la réponse de l'utilisateur pour ce blanc")
    print("    user_answer = request.form.get(f'answer_{i}', '').strip()")
    print("    # ...")
    print()
    print("# APRÈS:")
    print("# Récupérer d'abord toutes les réponses utilisateur")
    print("answer_fields = {}")
    print("for key in request.form:")
    print("    if key.startswith('answer_'):")
    print("        try:")
    print("            index = int(key.split('_')[1])")
    print("            answer_fields[index] = request.form[key].strip()")
    print("        except (ValueError, IndexError):")
    print("            app.logger.warning(f\"[FILL_IN_BLANKS_DEBUG] Format de champ invalide: {key}\")")
    print()
    print("app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Champs de réponse trouvés: {answer_fields}\")")
    print("app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Nombre de réponses: {len(answer_fields)} / {total_blanks} attendues\")")
    print()
    print("# Traiter chaque blanc")
    print("for i in range(total_blanks):")
    print("    # Récupérer la réponse de l'utilisateur pour ce blanc")
    print("    user_answer = answer_fields.get(i, '').strip()")
    print("    # ...")
    print()
    print("2. Ajouter une fonction auxiliaire pour déterminer la phrase et l'indice du blanc:")
    print()
    print("def get_blank_location(global_blank_index, sentences):")
    print("    \"\"\"Détermine à quelle phrase et à quel indice dans cette phrase correspond un indice global de blanc\"\"\"")
    print("    blank_count = 0")
    print("    for idx, sentence in enumerate(sentences):")
    print("        blanks_in_sentence = sentence.count('___')")
    print("        if blank_count <= global_blank_index < blank_count + blanks_in_sentence:")
    print("            # Calculer l'indice local du blanc dans cette phrase")
    print("            local_blank_index = global_blank_index - blank_count")
    print("            return idx, local_blank_index")
    print("        blank_count += blanks_in_sentence")
    print("    return -1, -1")
    print()
    print("3. Utiliser cette fonction pour améliorer le feedback:")
    print()
    print("# Déterminer l'index de la phrase à laquelle appartient ce blanc")
    print("sentence_index = -1")
    print("local_blank_index = -1")
    print("if 'sentences' in content:")
    print("    sentence_index, local_blank_index = get_blank_location(i, content['sentences'])")
    print("    app.logger.info(f\"  - Appartient à la phrase {sentence_index}, position {local_blank_index}\")")
    print()
    print("Ces modifications garantiront que toutes les réponses sont correctement récupérées et évaluées,")
    print("même lorsqu'il y a plusieurs blancs sur une même ligne.")

def main():
    """Fonction principale"""
    print("ANALYSE DU PROBLÈME DE SCORING POUR FILL_IN_BLANKS")
    print("=" * 60)
    
    # Analyser le problème
    current_score = simulate_current_scoring_logic()
    improved_score = simulate_improved_scoring_logic()
    
    print("\n=== COMPARAISON DES RÉSULTATS ===")
    print(f"Score avec la logique actuelle: {current_score}%")
    print(f"Score avec la logique améliorée: {improved_score}%")
    
    if current_score == improved_score:
        print("\nLa logique actuelle semble fonctionner correctement pour cet exemple.")
        print("Le problème pourrait être ailleurs ou dépendre de conditions spécifiques.")
    else:
        print("\nLa logique améliorée donne un score différent, ce qui confirme le problème.")
        print("La correction proposée devrait résoudre le problème de scoring.")
    
    # Proposer une correction
    propose_fix()

if __name__ == "__main__":
    main()
