import json
from app import app, db
from models import Exercise
from flask import render_template_string

def check_exercise_6_rendering():
    """
    Vérifie comment l'exercice ID 6 est rendu dans l'interface utilisateur.
    """
    with app.app_context():
        exercise = Exercise.query.get(6)
        if not exercise:
            print("Exercice ID 6 non trouvé!")
            return
        
        content = exercise.get_content()
        
        # Simuler le rendu de l'exercice comme dans app.py
        print("Simulation du rendu de l'exercice:")
        
        if 'sentences' in content:
            print("\nRendu des phrases:")
            for i, sentence in enumerate(content['sentences']):
                print(f"Phrase {i+1}: {sentence}")
                # Compter les blancs dans cette phrase
                blanks = sentence.count('___')
                print(f"  Nombre de blancs: {blanks}")
                
                # Simuler la transformation pour l'affichage HTML
                html_sentence = sentence.replace('___', '<span class="blank">___</span>')
                print(f"  HTML: {html_sentence}")
        
        if 'text' in content:
            print("\nRendu du texte:")
            text = content['text']
            print(f"Texte: {text}")
            blanks = text.count('___')
            print(f"  Nombre de blancs: {blanks}")
            
            # Simuler la transformation pour l'affichage HTML
            html_text = text.replace('___', '<span class="blank">___</span>')
            print(f"  HTML: {html_text}")
        
        # Vérifier la route de soumission dans app.py
        print("\nAnalyse de la logique de soumission:")
        print("Vérifions si le code de soumission traite correctement les blancs multiples...")
        
        # Simuler une soumission avec les deux réponses correctes
        answers = ["noir", "rouge"]
        print(f"Simulation de soumission avec réponses: {answers}")
        
        # Logique de scoring simplifiée
        correct_answers = content.get('answers', content.get('words', []))
        total_blanks_in_content = 0
        if 'sentences' in content:
            total_blanks_in_content = sum(s.count('___') for s in content['sentences'])
        elif 'text' in content:
            total_blanks_in_content = content['text'].count('___')
        
        total_blanks = max(total_blanks_in_content, len(correct_answers))
        
        # Simuler le comptage des réponses correctes
        correct_count = 0
        for i, answer in enumerate(answers):
            if i < len(correct_answers) and answer.lower() == correct_answers[i].lower():
                correct_count += 1
        
        score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        print(f"Score calculé: {correct_count}/{total_blanks} = {score}%")

if __name__ == "__main__":
    check_exercise_6_rendering()
