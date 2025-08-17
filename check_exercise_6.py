import json
from app import app, db
from models import Exercise

def check_exercise_6():
    """
    Examine la structure de l'exercice ID 6 pour comprendre le problème de scoring.
    """
    with app.app_context():
        exercise = Exercise.query.get(6)
        if not exercise:
            print("Exercice ID 6 non trouvé!")
            return
        
        print(f"Exercice ID: {exercise.id}")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        
        try:
            content = exercise.get_content()
            print("\nContenu brut:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
            
            print("\nAnalyse des blancs:")
            
            # Vérifier les phrases et compter les blancs
            if 'sentences' in content:
                sentences = content['sentences']
                print(f"Phrases: {sentences}")
                blanks_in_sentences = [s.count('___') for s in sentences]
                total_blanks_in_sentences = sum(blanks_in_sentences)
                print(f"Blancs dans les phrases: {blanks_in_sentences} (total: {total_blanks_in_sentences})")
            else:
                print("Pas de champ 'sentences' trouvé")
            
            # Vérifier le texte et compter les blancs
            if 'text' in content:
                text = content['text']
                print(f"Texte: {text}")
                blanks_in_text = text.count('___')
                print(f"Blancs dans le texte: {blanks_in_text}")
            else:
                print("Pas de champ 'text' trouvé")
            
            # Vérifier les mots disponibles
            if 'words' in content:
                print(f"Mots disponibles (words): {content['words']}")
            if 'available_words' in content:
                print(f"Mots disponibles (available_words): {content['available_words']}")
            
            # Vérifier les réponses
            if 'answers' in content:
                print(f"Réponses attendues: {content['answers']}")
            else:
                print("Pas de champ 'answers' trouvé")
            
            # Simuler la logique de scoring
            total_blanks_in_content = 0
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
            
            correct_answers = []
            if 'answers' in content:
                correct_answers = content['answers']
            elif 'words' in content:
                correct_answers = content['words']
            elif 'available_words' in content:
                correct_answers = content['available_words']
            
            total_blanks = max(total_blanks_in_content, len(correct_answers))
            print(f"\nLogique de scoring:")
            print(f"Total blancs dans le contenu: {total_blanks_in_content}")
            print(f"Nombre de réponses: {len(correct_answers)}")
            print(f"Total blancs pour scoring (max): {total_blanks}")
            print(f"Si toutes les réponses sont correctes: {total_blanks_in_content}/{total_blanks} = {(total_blanks_in_content/total_blanks)*100 if total_blanks > 0 else 0}%")
            
        except Exception as e:
            print(f"Erreur lors de l'analyse: {str(e)}")

if __name__ == "__main__":
    check_exercise_6()
