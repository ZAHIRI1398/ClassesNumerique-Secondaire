from app import app
from models import Exercise, db
import json

def create_test_qcm():
    with app.app_context():
        # Create a test QCM exercise
        qcm = Exercise(
            title='Test QCM',
            description='Test exercise',
            exercise_type='qcm',
            teacher_id=1
        )
        content = {
            'questions': [
                {
                    'text': 'Question 1',
                    'options': ['Option 1', 'Option 2'],
                    'correct_answer': '0'
                },
                {
                    'text': 'Question 2',
                    'options': ['Option A', 'Option B'],
                    'correct_answer': '1'
                }
            ]
        }
        qcm.content = json.dumps(content)
        db.session.add(qcm)
        db.session.commit()
        print(f'Created test QCM exercise with ID {qcm.id}')

        # Verify the content structure
        exercise = Exercise.query.filter_by(title='Test QCM').first()
        print('\nRaw content:', exercise.content)
        print('\nParsed content:', exercise.get_content())

if __name__ == '__main__':
    create_test_qcm()
