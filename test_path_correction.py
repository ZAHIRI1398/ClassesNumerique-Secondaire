"""
Script to test the automatic path correction for both /static/exercises/ and /static/uploads/ formats
"""

from flask import Flask
from models import db, Exercise
import json
import os
from utils.image_path_handler import normalize_image_path, fix_exercise_image_path, get_image_url
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def test_path_correction():
    """
    Test the automatic path correction for both path formats
    """
    with app.app_context():
        # Get all exercises
        exercises = Exercise.query.all()
        logger.info(f"Found {len(exercises)} exercises in the database")
        
        # Test each exercise
        for exercise in exercises:
            logger.info(f"\n--- Testing Exercise {exercise.id}: {exercise.title} ---")
            logger.info(f"Type: {exercise.exercise_type}")
            
            # Original paths
            original_image_path = exercise.image_path
            content = json.loads(exercise.content) if exercise.content else {}
            original_content_image = content.get('image')
            
            logger.info(f"Original image_path: {original_image_path}")
            logger.info(f"Original content image: {original_content_image}")
            
            # Test normalize_image_path
            if original_image_path:
                normalized_path = normalize_image_path(original_image_path)
                logger.info(f"Normalized image_path: {normalized_path}")
                
                # Check if normalization changed the path
                if normalized_path != original_image_path:
                    logger.info(f"Path was normalized from {original_image_path} to {normalized_path}")
                else:
                    logger.info(f"Path was already normalized: {normalized_path}")
            
            # Test fix_exercise_image_path
            modified = fix_exercise_image_path(exercise)
            if modified:
                logger.info(f"Exercise was modified by fix_exercise_image_path")
                logger.info(f"New image_path: {exercise.image_path}")
                
                # Check content
                content = json.loads(exercise.content) if exercise.content else {}
                logger.info(f"New content image: {content.get('image')}")
            else:
                logger.info(f"Exercise was not modified by fix_exercise_image_path")
            
            # Test get_image_url
            if original_image_path:
                image_url = get_image_url(original_image_path)
                logger.info(f"Image URL from original path: {image_url}")
                
                # Check if the URL was changed
                if image_url != original_image_path:
                    logger.info(f"URL was changed from {original_image_path} to {image_url}")
                else:
                    logger.info(f"URL remained the same: {image_url}")
            
            # Check if the image file exists
            if exercise.image_path:
                # Remove /static/ prefix to get the relative path
                relative_path = exercise.image_path.replace('/static/', '', 1)
                physical_path = os.path.join(app.root_path, 'static', *relative_path.split('/'))
                
                if os.path.exists(physical_path):
                    logger.info(f"[OK] Image exists at: {physical_path}")
                else:
                    logger.info(f"[ERROR] Image does not exist at: {physical_path}")
                    
                    # Check if it exists in the old path format
                    if '/uploads/' in exercise.image_path:
                        old_path = exercise.image_path.replace('/uploads/', '/exercises/', 1)
                        relative_old_path = old_path.replace('/static/', '', 1)
                        physical_old_path = os.path.join(app.root_path, 'static', *relative_old_path.split('/'))
                        
                        if os.path.exists(physical_old_path):
                            logger.info(f"[INFO] Image exists in old path format: {physical_old_path}")
                        else:
                            logger.info(f"[ERROR] Image does not exist in old path format either: {physical_old_path}")
            
            # Don't commit changes for this test
            db.session.rollback()
            
        logger.info("\n=== Test Complete ===")

if __name__ == "__main__":
    test_path_correction()
