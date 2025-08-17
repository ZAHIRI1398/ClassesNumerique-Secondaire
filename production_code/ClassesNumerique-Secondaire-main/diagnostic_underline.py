#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from app import app, Exercise, db

def analyze_underline_exercises():
    with app.app_context():
        exercises = Exercise.query.filter_by(exercise_type='underline_words').all()
        print(f'=== DIAGNOSTIC COMPLET: {len(exercises)} exercices "Souligner les mots" ===')
        
        working_exercises = []
        broken_exercises = []
        
        for exercise in exercises:
            print(f'\n--- EXERCICE {exercise.id}: {exercise.title} ---')
            try:
                content = json.loads(exercise.content)
                
                # Analyser la structure
                if 'words' in content:
                    words_data = content['words']
                    print(f'Structure: words (liste de {len(words_data)} elements)')
                    
                    # Vérifier si la structure est correcte
                    is_correct_structure = True
                    has_specific_words = True
                    
                    # Analyser chaque element
                    for i, word_item in enumerate(words_data[:3]):  # Afficher les 3 premiers
                        if isinstance(word_item, dict):
                            keys = list(word_item.keys())
                            print(f'  Element {i+1}: {keys}')
                            
                            if 'sentence' in word_item:
                                sentence = word_item['sentence'][:50] + '...' if len(word_item['sentence']) > 50 else word_item['sentence']
                                print(f'    Phrase: "{sentence}"')
                            else:
                                is_correct_structure = False
                                print(f'    PROBLEME: Pas de cle "sentence"')
                            
                            if 'words_to_underline' in word_item:
                                words = word_item['words_to_underline']
                                print(f'    Mots: {words} (type: {type(words).__name__}, count: {len(words) if isinstance(words, list) else "N/A"})')
                                
                                # Vérifier si tous les éléments ont la même liste (problème global)
                                if i == 0:
                                    first_words = words
                                elif words == first_words and len(words) > 2:
                                    has_specific_words = False
                                    print(f'    WARNING: Mots identiques à l\'element 1 (liste globale)')
                                    
                            elif 'text' in word_item:
                                is_correct_structure = False
                                print(f'    PROBLEME: Ancienne structure avec cle "text"')
                            else:
                                is_correct_structure = False
                                print(f'    PROBLEME: Pas de cle "words_to_underline"')
                        else:
                            is_correct_structure = False
                            print(f'  Element {i+1}: {type(word_item).__name__} - {str(word_item)[:50]}')
                    
                    if len(words_data) > 3:
                        print(f'  ... et {len(words_data) - 3} autres elements')
                    
                    # Classifier l'exercice
                    if is_correct_structure and has_specific_words:
                        working_exercises.append(exercise.id)
                        print(f'  STATUS: [OK] FONCTIONNEL')
                    else:
                        broken_exercises.append(exercise.id)
                        if not is_correct_structure:
                            print(f'  STATUS: [ERROR] STRUCTURE INCORRECTE')
                        elif not has_specific_words:
                            print(f'  STATUS: [ERROR] MOTS GLOBAUX (pas specifiques)')
                else:
                    broken_exercises.append(exercise.id)
                    print(f'Structure: [ERROR] PAS de cle "words" trouvee')
                    print(f'Cles disponibles: {list(content.keys())}')
                    
            except Exception as e:
                broken_exercises.append(exercise.id)
                print(f'[ERROR] ERREUR parsing JSON: {e}')
        
        print(f'\n=== RESUME FINAL ===')
        print(f'[OK] Exercices FONCTIONNELS: {working_exercises}')
        print(f'[ERROR] Exercices CASSES: {broken_exercises}')
        print(f'')
        print(f'RAPPORT UTILISATEUR:')
        print(f'- Exercices qui fonctionnent selon utilisateur: 7, 16, 23')
        print(f'- Exercices qui ne fonctionnent pas selon utilisateur: 22, 24')

if __name__ == '__main__':
    analyze_underline_exercises()
