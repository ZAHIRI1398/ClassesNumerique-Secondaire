"""
Script d'intégration du module d'inscription d'école dans l'application Flask.
Ce script modifie app.py pour importer et enregistrer le blueprint d'inscription d'école.
"""

import re
import sys
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'integrate_school_registration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

def integrate_school_registration():
    """
    Intègre le module d'inscription d'école dans app.py.
    """
    try:
        # Lecture du fichier app.py
        with open('app.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Vérifier si le module est déjà importé
        if 'from school_registration_mod import' in content:
            logger.info("Le module d'inscription d'école est déjà importé.")
            return
        
        # Ajouter l'import du module
        import_pattern = r'(# Import des modules.*?\n)'
        import_replacement = r'\1from school_registration_mod import init_app as init_school_registration\n'
        content = re.sub(import_pattern, import_replacement, content, flags=re.DOTALL)
        
        # Ajouter l'initialisation du module
        init_pattern = r'(# Initialisation des extensions.*?\n)'
        init_replacement = r'\1    # Initialisation du module d\'inscription d\'école\n    init_school_registration(app)\n'
        content = re.sub(init_pattern, init_replacement, content, flags=re.DOTALL)
        
        # Modifier la route register_school pour rediriger vers le blueprint
        register_school_pattern = r'@app\.route\(\'/register/school\', methods=\[\'GET\', \'POST\'\]\)\ndef register_school\(\):(.*?)return render_template\(.*?\)'
        register_school_replacement = r'@app.route(\'/register/school\', methods=[\'GET\', \'POST\'])\ndef register_school():\n    """Route d\'inscription pour les écoles (redirection vers le blueprint)"""\n    return redirect(url_for(\'school_registration_mod.register_school_simplified\'))'
        content = re.sub(register_school_pattern, register_school_replacement, content, flags=re.DOTALL)
        
        # Ajouter l'import de redirect et url_for s'ils ne sont pas déjà importés
        if 'from flask import ' in content and 'redirect' not in content:
            content = content.replace('from flask import ', 'from flask import redirect, url_for, ')
        
        # Sauvegarde du fichier modifié
        with open('app.py', 'w', encoding='utf-8') as file:
            file.write(content)
        
        logger.info("Module d'inscription d'école intégré avec succès dans app.py.")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'intégration du module d'inscription d'école: {str(e)}")
        return False

if __name__ == '__main__':
    logger.info("Début de l'intégration du module d'inscription d'école...")
    success = integrate_school_registration()
    if success:
        logger.info("Intégration terminée avec succès.")
    else:
        logger.error("Échec de l'intégration.")
        sys.exit(1)
