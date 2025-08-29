from fix_image_paths import image_sync_bp

def register_image_sync_routes(app):
    """
    Enregistre les routes de synchronisation et correction des chemins d'images
    dans l'application Flask.
    
    Args:
        app: L'application Flask
    """
    # Vérifier si le blueprint est déjà enregistré
    if 'image_sync' not in [bp.name for bp in app.blueprints.values()]:
        app.register_blueprint(image_sync_bp)
        app.logger.info("Routes de synchronisation et correction des chemins d'images enregistrées")
    else:
        app.logger.info("Routes de synchronisation d'images déjà enregistrées")
