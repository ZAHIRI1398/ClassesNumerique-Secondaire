import json
from flask import Flask
from app import app, db, Exercise

def fix_exercise_structure():
    """
    Corrige la structure de l'exercice à texte à trous ID 7
    pour séparer les phrases avec plusieurs blancs en phrases distinctes.
    """
    with app.app_context():
        # Récupérer l'exercice à texte à trous
        exercise_id = 7
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            print(f"Exercice ID {exercise_id} non trouvé")
            return
        
        print(f"Exercice ID {exercise_id}: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        
        try:
            content = json.loads(exercise.content)
            print("\nStructure actuelle du contenu:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
            
            # Créer la nouvelle structure
            new_content = {
                'sentences': []
            }
            
            # Traiter chaque phrase
            word_index = 0
            for sentence_index, sentence in enumerate(content['sentences']):
                # Compter les blancs dans la phrase
                blanks_count = sentence.count('___')
                print(f"\nPhrase {sentence_index+1}: {blanks_count} blancs")
                
                if blanks_count == 1:
                    # Si la phrase n'a qu'un seul blanc, l'ajouter telle quelle
                    if word_index < len(content['words']):
                        new_content['sentences'].append({
                            'text': sentence,
                            'answer': content['words'][word_index]
                        })
                        word_index += 1
                    else:
                        print(f"ATTENTION: Pas assez de mots pour la phrase {sentence_index+1}")
                
                elif blanks_count > 1:
                    # Si la phrase a plusieurs blancs, la diviser
                    print(f"Division de la phrase {sentence_index+1} avec {blanks_count} blancs")
                    
                    # Trouver les positions des blancs
                    blank_positions = []
                    start = 0
                    while True:
                        pos = sentence.find('___', start)
                        if pos == -1:
                            break
                        blank_positions.append(pos)
                        start = pos + 3
                    
                    # Créer une phrase distincte pour chaque blanc
                    for i, pos in enumerate(blank_positions):
                        # Déterminer le contexte avant et après le blanc
                        if i == 0:
                            before_text = sentence[:pos]
                        else:
                            before_text = sentence[blank_positions[i-1]+3:pos]
                        
                        if i == len(blank_positions) - 1:
                            after_text = sentence[pos+3:]
                        else:
                            after_text = sentence[pos+3:blank_positions[i+1]]
                        
                        # Créer la nouvelle phrase avec un seul blanc
                        new_text = before_text + '___' + after_text
                        
                        if word_index < len(content['words']):
                            new_content['sentences'].append({
                                'text': new_text,
                                'answer': content['words'][word_index]
                            })
                            word_index += 1
                        else:
                            print(f"ATTENTION: Pas assez de mots pour le blanc {i+1} de la phrase {sentence_index+1}")
            
            print("\nNouvelle structure du contenu:")
            print(json.dumps(new_content, indent=2, ensure_ascii=False))
            
            # Sauvegarder la nouvelle structure
            exercise.content = json.dumps(new_content, ensure_ascii=False)
            db.session.commit()
            print("\nExercice mis à jour avec la nouvelle structure")
            
        except json.JSONDecodeError:
            print(f"Erreur: Le contenu de l'exercice n'est pas un JSON valide")
            print(f"Contenu brut: {exercise.content}")

if __name__ == "__main__":
    fix_exercise_structure()
