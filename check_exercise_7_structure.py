import json
from flask import Flask
from app import app, db, Exercise

def check_exercise_structure():
    """
    Vérifie la structure de l'exercice à texte à trous ID 7
    pour comprendre pourquoi un seul blanc est compté dans la première ligne.
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
            
            # Analyser la structure des phrases
            if 'sentences' in content and isinstance(content['sentences'], list):
                print(f"\nNombre total de phrases: {len(content['sentences'])}")
                
                for i, sentence in enumerate(content['sentences']):
                    print(f"\nPhrase {i+1}:")
                    
                    if isinstance(sentence, dict):
                        print(f"Type: dictionnaire")
                        
                        if 'text' in sentence:
                            print(f"Texte: {sentence['text']}")
                            # Compter les blancs dans le texte
                            blanks_count = sentence['text'].count('___')
                            print(f"Nombre de blancs dans le texte: {blanks_count}")
                        else:
                            print("Pas de clé 'text'")
                        
                        if 'answer' in sentence:
                            print(f"Réponse: {sentence['answer']}")
                        else:
                            print("Pas de clé 'answer'")
                    else:
                        print(f"Type: {type(sentence).__name__}")
                        print(f"Contenu: {sentence}")
                        
                        # Si c'est une chaîne, compter les blancs
                        if isinstance(sentence, str):
                            blanks_count = sentence.count('___')
                            print(f"Nombre de blancs dans la phrase: {blanks_count}")
            
            # Vérifier si le problème est que la première phrase a deux blancs mais une seule réponse
            if 'sentences' in content and len(content['sentences']) > 0:
                first_sentence = content['sentences'][0]
                
                if isinstance(first_sentence, dict) and 'text' in first_sentence:
                    blanks_in_first = first_sentence['text'].count('___')
                    print(f"\nLa première phrase contient {blanks_in_first} blancs mais une seule réponse")
                    
                    if blanks_in_first > 1:
                        print("PROBLÈME IDENTIFIÉ: La première phrase contient plusieurs blancs mais une seule réponse")
                        print("Le code de soumission ne peut pas gérer plusieurs blancs dans une seule phrase")
                        
                        # Proposer une correction
                        print("\nCorrection proposée:")
                        print("Diviser la première phrase en plusieurs phrases, une pour chaque blanc")
                
        except json.JSONDecodeError:
            print(f"Erreur: Le contenu de l'exercice n'est pas un JSON valide")
            print(f"Contenu brut: {exercise.content}")

if __name__ == "__main__":
    check_exercise_structure()
