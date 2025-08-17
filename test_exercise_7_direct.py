import json
import sys
from flask import Flask, request
from app import app, db, Exercise

def test_exercise_scoring():
    """
    Test direct du scoring de l'exercice 7 (texte à trous)
    en simulant une soumission de formulaire avec toutes les réponses correctes.
    """
    with app.app_context():
        # Récupérer l'exercice
        exercise_id = 7
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            print(f"Exercice ID {exercise_id} non trouvé")
            return
        
        print(f"Exercice ID {exercise_id}: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        
        try:
            content = json.loads(exercise.content)
            print("\nContenu:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
            
            # Compter les blancs dans le contenu
            total_blanks_in_content = 0
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
                print(f"\nNombre de blancs dans 'sentences': {sentences_blanks}")
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
                print(f"\nNombre de blancs dans 'text': {text_blanks}")
            
            # Récupérer les réponses correctes
            correct_answers = content.get('words', []) or content.get('available_words', [])
            print(f"\nRéponses correctes: {correct_answers}")
            print(f"Nombre de réponses correctes: {len(correct_answers)}")
            
            # Simuler une soumission de formulaire avec toutes les réponses correctes
            form_data = {}
            for i, answer in enumerate(correct_answers):
                form_data[f'answer_{i}'] = answer
            
            print("\nDonnées du formulaire simulé:")
            for key, value in form_data.items():
                print(f"{key}: {value}")
            
            # Simuler le calcul du score
            total_blanks = max(total_blanks_in_content, len(correct_answers))
            correct_blanks = 0
            feedback_details = []
            
            # Vérifier chaque blanc individuellement
            for i in range(total_blanks):
                # Récupérer la réponse de l'utilisateur pour ce blanc
                user_answer = form_data.get(f'answer_{i}', '').strip()
                
                # Récupérer la réponse correcte correspondante
                correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                
                print(f"\nBlanc {i}:")
                print(f"  - Réponse simulée: '{user_answer}'")
                print(f"  - Réponse correcte: '{correct_answer}'")
                
                # Vérifier si la réponse est correcte (insensible à la casse)
                is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
                if is_correct:
                    correct_blanks += 1
                    print(f"  - CORRECT")
                else:
                    print(f"  - INCORRECT")
                
                # Créer le feedback pour ce blanc
                feedback_details.append({
                    'blank_index': i,
                    'user_answer': user_answer or '',
                    'correct_answer': correct_answer,
                    'is_correct': is_correct
                })
            
            # Calculer le score final
            score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
            
            print(f"\nScore final: {score}% ({correct_blanks}/{total_blanks})")
            
            if score == 100:
                print("\nSUCCÈS: Le score est de 100% comme attendu.")
            else:
                print(f"\nPROBLÈME: Le score est de {score}% au lieu de 100%.")
                print("Vérifiez le code de scoring dans app.py et le format du contenu de l'exercice.")
            
        except json.JSONDecodeError:
            print(f"Erreur: Le contenu de l'exercice n'est pas un JSON valide")
            print(f"Contenu brut: {exercise.content}")
        except Exception as e:
            print(f"Erreur inattendue: {str(e)}")

if __name__ == "__main__":
    test_exercise_scoring()
