"""
Script pour vérifier les routes enregistrées dans l'application Flask
"""
import sys
import os
from importlib import import_module
from flask import Flask, url_for

# Créer une application Flask minimale pour tester
app = Flask(__name__, template_folder='templates')
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'test-key'

# Importer le fichier app.py sans l'exécuter directement
sys.path.insert(0, os.path.abspath('.'))
try:
    # Charger le module app.py
    app_module = import_module('app')
    
    # Récupérer les routes définies dans app.py
    print("=== ROUTES DÉFINIES DANS APP.PY ===")
    for attr_name in dir(app_module):
        attr = getattr(app_module, attr_name)
        if callable(attr) and hasattr(attr, '__name__'):
            if attr.__name__ == 'register_school':
                print(f"Route 'register_school' trouvée dans app.py")
                # Vérifier si la route est décorée avec app.route
                if hasattr(attr, 'view_class') or hasattr(attr, '__wrapped__'):
                    print("La route est correctement décorée avec @app.route")
                else:
                    print("ATTENTION: La route n'est pas correctement décorée avec @app.route")
    
    # Tester si la route register_school est accessible
    with app.test_request_context():
        try:
            # Essayer d'obtenir l'URL pour register_school
            url = url_for('register_school')
            print(f"URL pour register_school: {url}")
        except Exception as e:
            print(f"Erreur lors de la génération de l'URL pour register_school: {str(e)}")
            print("La route register_school n'est pas correctement enregistrée dans l'application Flask.")
    
    # Vérifier si d'autres routes sont définies
    print("\n=== TOUTES LES ROUTES DÉFINIES ===")
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint} -> {rule}")
    
except Exception as e:
    print(f"Erreur lors de l'importation de app.py: {str(e)}")

# Tester avec une application Flask minimale
print("\n=== TEST AVEC UNE APPLICATION FLASK MINIMALE ===")
test_app = Flask(__name__, template_folder='templates')

@test_app.route('/register/school')
def register_school():
    return "Test route"

with test_app.test_request_context():
    try:
        url = url_for('register_school')
        print(f"URL pour register_school dans l'application de test: {url}")
    except Exception as e:
        print(f"Erreur dans l'application de test: {str(e)}")

print("\n=== VÉRIFICATION DU TEMPLATE LOGIN.HTML ===")
if os.path.exists('templates/login.html'):
    with open('templates/login.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'url_for(\'register_school\')' in content:
            print("La référence à register_school est présente dans le template login.html")
            # Trouver les lignes contenant register_school
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'url_for(\'register_school\')' in line:
                    print(f"Ligne {i+1}: {line.strip()}")
        else:
            print("La référence à register_school n'est pas présente dans le template login.html")
else:
    print("Le fichier templates/login.html n'existe pas")
