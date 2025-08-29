from flask import Flask
from models import db, Exercise
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def verify_all_exercises():
    """
    Verify all exercises in the database and check their image paths
    """
    with app.app_context():
        # Get all exercises
        exercises = Exercise.query.all()
        print(f"Found {len(exercises)} exercises in the database")
        
        issues_found = 0
        
        for exercise in exercises:
            print(f"\n--- Exercise {exercise.id}: {exercise.title} ---")
            print(f"Type: {exercise.exercise_type}")
            
            # Check if image_path exists
            if exercise.image_path:
                print(f"Image path: {exercise.image_path}")
                
                # Check if image_path starts with /static/
                if not exercise.image_path.startswith('/static/'):
                    print(f"[ERROR] Image path does not start with /static/: {exercise.image_path}")
                    issues_found += 1
                
                # Check if the image exists physically
                relative_path = exercise.image_path.replace('/static/', '', 1)
                physical_path = os.path.join(app.root_path, 'static', *relative_path.split('/'))
                
                if os.path.exists(physical_path):
                    print(f"[OK] Image exists at: {physical_path}")
                else:
                    print(f"[ERROR] Image does not exist at: {physical_path}")
                    issues_found += 1
            else:
                print("[INFO] No image_path set for this exercise")
            
            # Check content JSON for image paths
            if exercise.content:
                try:
                    content = json.loads(exercise.content)
                    if 'image' in content:
                        print(f"Content image path: {content['image']}")
                        
                        # Check if content image path matches exercise.image_path
                        if exercise.image_path and content['image'] != exercise.image_path:
                            print(f"[ERROR] Content image path does not match exercise.image_path")
                            print(f"  - exercise.image_path: {exercise.image_path}")
                            print(f"  - content['image']: {content['image']}")
                            issues_found += 1
                        
                        # Check if content image path starts with /static/
                        if not content['image'].startswith('/static/'):
                            print(f"[ERROR] Content image path does not start with /static/: {content['image']}")
                            issues_found += 1
                    else:
                        print("[INFO] No image in content JSON")
                except json.JSONDecodeError:
                    print("[ERROR] Invalid JSON content")
                    issues_found += 1
            else:
                print("[INFO] No content JSON")
        
        # Summary
        print("\n=== Summary ===")
        print(f"Total exercises: {len(exercises)}")
        print(f"Issues found: {issues_found}")
        
        if issues_found == 0:
            print("[SUCCESS] All image paths are correctly configured!")
        else:
            print(f"[WARNING] Found {issues_found} issues with image paths")

if __name__ == "__main__":
    verify_all_exercises()
