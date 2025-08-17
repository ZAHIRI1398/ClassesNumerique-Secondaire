import json
from flask import Flask
from app import app, db, Exercise

def check_exercise_structure():
    """
    Vérifie la structure de l'exercice à texte à trous ID 7
    et la compare avec ce que le code de soumission attend.
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
            
            # Vérifier la structure attendue par le code de soumission
            if 'sentences' in content:
                print("\nVérification de la structure 'sentences':")
                if isinstance(content['sentences'], list):
                    print("OK - 'sentences' est une liste")
                    
                    for i, sentence in enumerate(content['sentences']):
                        print(f"\nPhrase {i+1}:")
                        if isinstance(sentence, dict):
                            print("OK - La phrase est un dictionnaire")
                            if 'text' in sentence:
                                print(f"OK - Clé 'text' présente: {sentence['text']}")
                            else:
                                print("ERREUR - Clé 'text' manquante")
                            
                            if 'answer' in sentence:
                                print(f"OK - Clé 'answer' présente: {sentence['answer']}")
                            else:
                                print("ERREUR - Clé 'answer' manquante")
                        else:
                            print(f"ERREUR - La phrase est de type {type(sentence).__name__}, mais devrait être un dictionnaire")
                            print(f"  Valeur: {sentence}")
                else:
                    print(f"ERREUR - 'sentences' est de type {type(content['sentences']).__name__}, mais devrait être une liste")
            else:
                print("ERREUR - Clé 'sentences' manquante dans le contenu")
            
            # Vérifier la présence de 'words'
            if 'words' in content:
                print("\nVérification de la structure 'words':")
                if isinstance(content['words'], list):
                    print(f"OK - 'words' est une liste: {content['words']}")
                else:
                    print(f"ERREUR - 'words' est de type {type(content['words']).__name__}, mais devrait être une liste")
            else:
                print("ERREUR - Clé 'words' manquante dans le contenu")
            
            # Proposer une structure corrigée
            print("\nStructure attendue par le code de soumission:")
            corrected_content = {
                'sentences': []
            }
            
            if 'sentences' in content and isinstance(content['sentences'], list):
                for i, sentence in enumerate(content['sentences']):
                    if isinstance(sentence, str):
                        # Extraire les parties de la phrase (avant/après les blancs)
                        parts = sentence.split('___')
                        
                        # Créer une phrase avec la structure attendue
                        corrected_sentence = {
                            'text': sentence,  # Garder la phrase originale avec les blancs
                            'answer': content['words'][i] if 'words' in content and i < len(content['words']) else f"réponse_{i}"
                        }
                        
                        corrected_content['sentences'].append(corrected_sentence)
            
            print(json.dumps(corrected_content, indent=2, ensure_ascii=False))
            
        except json.JSONDecodeError:
            print(f"Erreur: Le contenu de l'exercice n'est pas un JSON valide")
            print(f"Contenu brut: {exercise.content}")

if __name__ == "__main__":
    check_exercise_structure()
