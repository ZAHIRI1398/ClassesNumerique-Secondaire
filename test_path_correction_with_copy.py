"""
Script to test the automatic path correction for both /static/exercises/ and /static/uploads/ formats
with automatic copying of images from old path to new path
"""

from flask import Flask
from models import db, Exercise
import json
import os
import shutil
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

def ensure_directory_exists(path):
    """Ensure the directory for the given file path exists"""
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def test_path_correction_with_copy():
    """
    Test the automatic path correction for both path formats
    and copy images from old path to new path if needed
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
                    
                    # Check if the image exists in the old path
                    old_relative_path = original_image_path.replace('/static/', '', 1)
                    old_physical_path = os.path.join(app.root_path, 'static', *old_relative_path.split('/'))
                    
                    # Check if the image exists in the new path
                    new_relative_path = normalized_path.replace('/static/', '', 1)
                    new_physical_path = os.path.join(app.root_path, 'static', *new_relative_path.split('/'))
                    
                    if os.path.exists(old_physical_path) and not os.path.exists(new_physical_path):
                        # Copy the image from old path to new path
                        ensure_directory_exists(new_physical_path)
                        shutil.copy2(old_physical_path, new_physical_path)
                        logger.info(f"Copied image from {old_physical_path} to {new_physical_path}")
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
                
                # Save changes to database
                db.session.commit()
                logger.info(f"Changes saved to database")
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
                            
                            # Copy the image from old path to new path
                            ensure_directory_exists(physical_path)
                            shutil.copy2(physical_old_path, physical_path)
                            logger.info(f"Copied image from {physical_old_path} to {physical_path}")
                        else:
                            logger.info(f"[ERROR] Image does not exist in old path format either: {physical_old_path}")
                            
                            # Check if it exists in the original path with qcm subdirectory
                            if exercise.exercise_type == 'qcm':
                                old_path_with_subdir = exercise.image_path.replace('/static/uploads/', '/static/exercises/qcm/', 1)
                                relative_old_path_with_subdir = old_path_with_subdir.replace('/static/', '', 1)
                                physical_old_path_with_subdir = os.path.join(app.root_path, 'static', *relative_old_path_with_subdir.split('/'))
                                
                                if os.path.exists(physical_old_path_with_subdir):
                                    logger.info(f"[INFO] Image exists in old path with subdirectory: {physical_old_path_with_subdir}")
                                    
                                    # Copy the image from old path to new path
                                    ensure_directory_exists(physical_path)
                                    shutil.copy2(physical_old_path_with_subdir, physical_path)
                                    logger.info(f"Copied image from {physical_old_path_with_subdir} to {physical_path}")
            
        logger.info("\n=== Test Complete ===")

if __name__ == "__main__":
    test_path_correction_with_copy()
