from blueprints.school_registration_mod import register_blueprint 
 
def integrate_school_registration_mod(app): 
    """Intègre la modification de la route d'inscription d'école""" 
    register_blueprint(app) 
    app.logger.info("Route d'inscription d'école modifiée intégrée avec succès") 
    return True 
