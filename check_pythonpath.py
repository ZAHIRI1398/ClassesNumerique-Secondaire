"""
Script pour vérifier le PYTHONPATH et l'importation des modules en production.
Ce script crée un endpoint de diagnostic qui affiche les informations sur l'environnement Python.
"""

from flask import Blueprint, render_template, jsonify, current_app
import sys
import os
import inspect

# Créer un blueprint pour le diagnostic
check_pythonpath_bp = Blueprint('check_pythonpath', __name__, url_prefix='/diagnose')

@check_pythonpath_bp.route('/pythonpath')
def check_pythonpath():
    """Endpoint pour vérifier le PYTHONPATH et les modules importables."""
    # Collecter les informations sur l'environnement
    info = {
        'sys_path': sys.path,
        'current_directory': os.getcwd(),
        'python_version': sys.version,
        'module_locations': {}
    }
    
    # Essayer d'importer les modules blueprint
    modules_to_check = [
        'diagnose_select_school_route',
        'fix_payment_select_school'
    ]
    
    for module_name in modules_to_check:
        try:
            module = __import__(module_name)
            info['module_locations'][module_name] = {
                'found': True,
                'path': inspect.getfile(module),
                'dir': os.path.dirname(inspect.getfile(module))
            }
        except ImportError as e:
            info['module_locations'][module_name] = {
                'found': False,
                'error': str(e)
            }
    
    # Vérifier si les fichiers existent dans le répertoire courant
    for module_name in modules_to_check:
        file_name = f"{module_name}.py"
        file_path = os.path.join(os.getcwd(), file_name)
        info[f"{module_name}_file_exists"] = os.path.isfile(file_path)
        info[f"{module_name}_file_path"] = file_path
    
    # Renvoyer les informations au format JSON
    return jsonify(info)

def integrate_pythonpath_check(app):
    """Intègre le blueprint de vérification du PYTHONPATH dans l'application Flask."""
    app.register_blueprint(check_pythonpath_bp)
    print("Blueprint de vérification du PYTHONPATH intégré avec succès.")
    return True

if __name__ == "__main__":
    print("Ce script doit être importé et utilisé avec une application Flask.")
    print("Exemple d'utilisation:")
    print("from check_pythonpath import integrate_pythonpath_check")
    print("integrate_pythonpath_check(app)")
