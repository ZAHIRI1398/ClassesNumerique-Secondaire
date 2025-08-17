import json
from flask import Flask
from app import app, db, Exercise

def test_fixed_structure():
    """
    Teste si la structure corrigée de l'exercice résout le problème de scoring.
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
            
            # Vérifier le nombre de phrases
            if 'sentences' in content and isinstance(content['sentences'], list):
                num_sentences = len(content['sentences'])
                print(f"\nNombre de phrases: {num_sentences}")
                
                # Vérifier le nombre de blancs dans chaque phrase
                total_blanks = 0
                for i, sentence in enumerate(content['sentences']):
                    if isinstance(sentence, dict) and 'text' in sentence:
                        blanks_count = sentence['text'].count('___')
                        total_blanks += blanks_count
                        print(f"Phrase {i+1}: {blanks_count} blancs")
                
                print(f"\nNombre total de blancs: {total_blanks}")
                
                # Simuler une soumission avec toutes les réponses correctes
                form_data = {}
                for i in range(num_sentences):
                    if isinstance(content['sentences'][i], dict) and 'answer' in content['sentences'][i]:
                        answer = content['sentences'][i]['answer']
                        form_data[f'answer_{i}'] = answer
                
                print("\nDonnées du formulaire simulées:")
                print(json.dumps(form_data, indent=2, ensure_ascii=False))
                
                # Simuler le traitement des réponses
                total_questions = num_sentences
                correct_answers = 0
                feedback = []
                
                for i in range(total_questions):
                    student_answer = form_data.get(f'answer_{i}')
                    correct_answer = content['sentences'][i]['answer']
                    print(f"\nQuestion {i + 1}:")
                    print(f"- Réponse soumise : {student_answer}")
                    print(f"- Réponse correcte : {correct_answer}")
                    
                    if student_answer and student_answer.strip().lower() == correct_answer.strip().lower():
                        correct_answers += 1
                        print("- Résultat: CORRECT")
                        feedback.append({
                            'question': content['sentences'][i]['text'],
                            'student_answer': student_answer,
                            'correct_answer': correct_answer,
                            'is_correct': True
                        })
                    else:
                        print("- Résultat: INCORRECT")
                        feedback.append({
                            'question': content['sentences'][i]['text'],
                            'student_answer': student_answer or '',
                            'correct_answer': correct_answer,
                            'is_correct': False
                        })
                
                score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
                print(f"\nScore calculé: {score}% ({correct_answers}/{total_questions})")
                
                # Afficher le feedback
                print("\nFeedback détaillé:")
                for i, item in enumerate(feedback):
                    print(f"Question {i + 1}: {item['question']}")
                    print(f"- Réponse soumise: {item['student_answer']}")
                    print(f"- Réponse correcte: {item['correct_answer']}")
                    print(f"- Résultat: {'CORRECT' if item['is_correct'] else 'INCORRECT'}")
            
        except json.JSONDecodeError:
            print(f"Erreur: Le contenu de l'exercice n'est pas un JSON valide")
            print(f"Contenu brut: {exercise.content}")

if __name__ == "__main__":
    test_fixed_structure()
