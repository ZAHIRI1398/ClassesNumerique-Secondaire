"""
Module pour enregistrer le service d'images unifié comme helper de template dans Flask
"""

from unified_image_service import get_cloudinary_url, image_service

def register_unified_image_service(app):
    """
    Enregistre le service d'images unifié comme helper de template dans Flask
    
    Args:
        app: Application Flask
    """
    # Enregistrer la fonction get_image_url comme helper global
    app.jinja_env.globals.update(get_image_url=image_service.get_image_url)
    
    # Conserver get_cloudinary_url pour la rétrocompatibilité
    app.jinja_env.globals.update(get_cloudinary_url=get_cloudinary_url)
    
    # Enregistrer le service complet pour un accès à toutes ses méthodes
    app.jinja_env.globals.update(image_service=image_service)
    
    return True
