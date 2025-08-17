import json
from flask import Flask
from app import app, db, Exercise

def fix_exercise_structure():
    """
    Corrige la structure de l'exercice à texte à trous ID 7
    pour qu'elle corresponde à ce que le code de soumission attend.
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
            
            # Si nous avons une seule phrase avec plusieurs blancs
            if 'sentences' in content and isinstance(content['sentences'], list) and len(content['sentences']) == 1:
                sentence = content['sentences'][0]
                
                # Diviser la phrase en fonction des blancs
                if isinstance(sentence, str) and '___' in sentence:
                    # Extraire les blancs de la phrase
                    blanks = sentence.split('___')
                    num_blanks = len(blanks) - 1  # Le nombre de blancs est le nombre de parties - 1
                    
                    print(f"\nNombre de blancs détectés: {num_blanks}")
                    
                    # Vérifier si nous avons les réponses pour chaque blanc
                    if 'words' in content and isinstance(content['words'], list):
                        print(f"Nombre de réponses disponibles: {len(content['words'])}")
                        
                        # Créer une entrée pour chaque blanc avec sa réponse
                        for i in range(min(num_blanks, len(content['words']))):
                            # Créer une phrase avec un seul blanc
                            blank_text = f"{blanks[i]}___{blanks[i+1] if i+1 < len(blanks) else ''}"
                            
                            new_sentence = {
                                'text': blank_text.strip(),
                                'answer': content['words'][i]
                            }
                            
                            new_content['sentences'].append(new_sentence)
                    else:
                        print("ERREUR: Pas de réponses disponibles dans 'words'")
            
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
