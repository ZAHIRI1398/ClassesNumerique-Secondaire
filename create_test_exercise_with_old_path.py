from flask import Flask
from models import db, User, Exercise
import json
import os
import shutil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Get the teacher user
    teacher = User.query.filter_by(role="teacher").first()
    if not teacher:
        print("No teacher user found. Please run init_exercises.py first.")
        exit(1)
    
    # Create a test exercise with image path in /static/exercises/ format
    test_qcm = Exercise(
        title="Test QCM with Old Path Format",
        description="This exercise uses the old /static/exercises/ path format",
        exercise_type="qcm",
        image_path="/static/exercises/qcm/test_old_path.png",  # Old format
        content=json.dumps({
            "image": "/static/exercises/qcm/test_old_path.png",  # Old format
            "questions": [
                {
                    "text": "What is 2+2?",
                    "choices": ["3", "4", "5"],
                    "correct_answer": 1
                },
                {
                    "text": "What is 3×3?",
                    "choices": ["6", "9", "12"],
                    "correct_answer": 1
                }
            ]
        }),
        teacher_id=teacher.id
    )
    db.session.add(test_qcm)
    db.session.commit()
    
    # Create the test image in both directories to test fallback
    os.makedirs(os.path.join(app.root_path, 'static', 'exercises', 'qcm'), exist_ok=True)
    
    # Create the test image
    def create_test_image(path, text):
        # Try to use PIL if available
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a new image with a light blue background
            width, height = 600, 300
            image = Image.new('RGB', (width, height), (200, 220, 255))
            draw = ImageDraw.Draw(image)
            
            # Draw a border
            border_width = 5
            draw.rectangle(
                [(border_width, border_width), (width - border_width, height - border_width)],
                outline=(0, 0, 200),
                width=border_width
            )
            
            # Try to use a standard font
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except IOError:
                font = ImageFont.load_default()
            
            # Calculate text position to center it
            text_width = draw.textlength(text, font=font)
            text_position = ((width - text_width) / 2, height / 2 - 18)
            
            # Draw the text
            draw.text(text_position, text, fill=(0, 0, 0), font=font)
            
            # Save the image
            image.save(path)
            print(f"Image created: {path}")
            
        except ImportError:
            # If PIL is not available, create an empty file
            with open(path, 'wb') as f:
                f.write(b'')
            print(f"Empty image placeholder created: {path}")
    
    # Create the test image in the old path format
    old_path = os.path.join(app.root_path, 'static', 'exercises', 'qcm', 'test_old_path.png')
    create_test_image(old_path, "TEST IMAGE - OLD PATH FORMAT")
    
    print(f"Test exercise created with ID: {test_qcm.id}")
    print(f"Image path: {test_qcm.image_path}")
    print(f"Physical image path: {old_path}")
