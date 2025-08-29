"""
Template helpers for consistent image handling across all templates
"""

from utils.image_path_manager import get_image_display_path, ImagePathManager
import json

def get_exercise_image_url(exercise, content=None):
    """
    Helper function for templates to get the correct image URL for an exercise
    
    Args:
        exercise: Exercise object
        content: Content dict or JSON string (optional)
        
    Returns:
        str: Image URL for display or None
    """
    return get_image_display_path(exercise, content)

def get_content_image_url(content, field_name='image'):
    """
    Helper function to get image URL from content dict
    
    Args:
        content: Content dict or JSON string
        field_name: Name of the image field to look for
        
    Returns:
        str: Image URL or None
    """
    if not content:
        return None
        
    # Parse JSON string if needed
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return None
    
    if not isinstance(content, dict):
        return None
        
    # Look for the specified field
    if field_name in content and content[field_name]:
        return ImagePathManager.clean_duplicate_paths(content[field_name])
        
    return None

def register_template_helpers(app):
    """
    Register template helper functions with Flask app
    
    Args:
        app: Flask application instance
    """
    app.jinja_env.globals['get_exercise_image_url'] = get_exercise_image_url
    app.jinja_env.globals['get_content_image_url'] = get_content_image_url
