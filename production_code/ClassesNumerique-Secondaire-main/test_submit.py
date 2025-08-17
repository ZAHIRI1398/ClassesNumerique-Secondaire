from flask import Flask
from models import db, Exercise, ExerciseAttempt, User
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def test_submit_answer():
    with app.app_context():
        # Créer un utilisateur de test s'il n'existe pas
        user = User.query.filter_by(username='test_student').first()
        if not user:
            from werkzeug.security import generate_password_hash
            user = User(
                username='test_student',
                email='test@example.com',
                password_hash=generate_password_hash('test123'),
                role='student',
                name='Test Student'
            )
            db.session.add(user)
            db.session.commit()
        
        # Récupérer l'exercice de test
        exercise = Exercise.query.filter_by(title='Test Texte à Trous').first()
        if not exercise:
            print("Exercice de test non trouvé")
            return
        
        # Simuler une soumission de réponse
        answers = {
            'answer_0': 'ciel',    # Réponse correcte
            'answer_1': 'maison'   # Réponse incorrecte
        }
        
        # Créer une tentative
        attempt = ExerciseAttempt(
            exercise_id=exercise.id,
            student_id=user.id,
            answers=json.dumps(answers)
        )
        
        # Calculer le score et le feedback
        content = json.loads(exercise.content)
        feedback = []
        correct_count = 0
        total_blanks = len(content['sentences'])
        
        for i, sentence in enumerate(content['sentences']):
            answer = answers.get(f'answer_{i}')
            reconstructed = sentence.replace('___', answer if answer else '')
            is_correct = answer in content['words'] and reconstructed.strip() == sentence.replace('___', answer).strip()
            
            if is_correct:
                correct_count += 1
            
            feedback.append({
                'sentence': sentence,
                'student_answer': answer,
                'is_correct': is_correct
            })
        
        score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        attempt.score = score
        attempt.feedback = json.dumps(feedback)
        
        db.session.add(attempt)
        db.session.commit()
        
        print(f"Tentative créée avec ID: {attempt.id}")
        print(f"Score: {score}%")
        print("\nFeedback:")
        for item in feedback:
            print(f"Phrase: {item['sentence']}")
            print(f"Réponse: {item['student_answer']}")
            print(f"Correct: {'Oui' if item['is_correct'] else 'Non'}")
            print("-" * 30)

if __name__ == '__main__':
    test_submit_answer()
