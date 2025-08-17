from app import app
from models import db, Exercise
import json

def fix_qcm_content(exercise_id=None):
    """Fix QCM content structure for a specific exercise or all QCM exercises"""
    with app.app_context():
        if exercise_id:
            exercises = [Exercise.query.get(exercise_id)]
        else:
            exercises = Exercise.query.filter_by(exercise_type='qcm').all()
        
        for exercise in exercises:
            if not exercise or exercise.exercise_type != 'qcm':
                continue
                
            print(f"\nAnalyzing QCM exercise {exercise.id}: {exercise.title}")
            print(f"Raw content: {exercise.content}")
            
            try:
                # Parse raw content first
                raw_content = exercise.content
                if not raw_content:
                    raw_content = '{}'
                
                try:
                    content = json.loads(raw_content)
                    print("Raw JSON structure:", json.dumps(content, indent=2))
                except json.JSONDecodeError:
                    print("Warning: Raw content is not valid JSON, attempting to fix")
                    try:
                        # Try to fix single quotes
                        content = eval(raw_content)
                        print("Fixed JSON structure:", json.dumps(content, indent=2))
                    except:
                        print("Could not parse content, using empty dict")
                        content = {}
                
                # Ensure questions list exists
                if 'questions' not in content:
                    content['questions'] = []
                    print("Added missing 'questions' list")
                
                # Fix each question's structure
                fixed_questions = []
                for i, q in enumerate(content.get('questions', [])):
                    print(f"\nProcessing question {i+1}:")
                    print("Original structure:", json.dumps(q, indent=2))
                    
                    if not isinstance(q, dict):
                        print(f"❌ Question has invalid format (not a dict), skipping")
                        continue
                    
                    # Map fields
                    text = q.get('text', '') or q.get('question', '')
                    options = q.get('options', []) or q.get('choices', [])
                    correct = str(q.get('correct_answer', None) if q.get('correct_answer') is not None else q.get('correct', '0'))
                    
                    print(f"Found text: {text}")
                    print(f"Found options: {options}")
                    print(f"Found correct answer: {correct}")
                    
                    fixed_question = {
                        'text': text,
                        'options': options,
                        'correct_answer': correct
                    }
                    
                    # Validate question structure
                    if fixed_question['text'] and fixed_question['options']:
                        fixed_questions.append(fixed_question)
                        print("✓ Question fixed and added")
                    else:
                        print("❌ Question invalid (missing text or options), skipping")
                
                # Update content if changes were made
                if fixed_questions:
                    content['questions'] = fixed_questions
                    exercise.content = json.dumps(content)
                    db.session.commit()
                    print(f"\n✓ Updated exercise {exercise.id} with {len(fixed_questions)} valid questions")
                    print("New content:", json.dumps(content, indent=2))
                else:
                    print(f"\n❌ No valid questions found for exercise {exercise.id}")
                    
            except Exception as e:
                print(f"Error processing exercise {exercise.id}: {str(e)}")
                import traceback
                print("Full error:", traceback.format_exc())
                db.session.rollback()

if __name__ == '__main__':
    # Fix all QCM exercises
    fix_qcm_content()
