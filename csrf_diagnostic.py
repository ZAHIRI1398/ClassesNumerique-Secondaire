from flask import Flask, render_template_string, request, flash, redirect, url_for, session
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('csrf_diagnostic')

# Création de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'diagnostic-secret-key'
app.config['DEBUG'] = True

# Initialisation de la protection CSRF
csrf = CSRFProtect(app)

# Template HTML pour le formulaire de test
form_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Test CSRF</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .form-group { margin-bottom: 15px; }
        .btn { padding: 10px 15px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        .flash { padding: 10px; margin-bottom: 15px; border-radius: 5px; }
        .flash.success { background-color: #dff0d8; border: 1px solid #d6e9c6; color: #3c763d; }
        .flash.error { background-color: #f2dede; border: 1px solid #ebccd1; color: #a94442; }
        .debug-info { background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; margin-top: 20px; }
        pre { white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Diagnostic CSRF</h1>
        
        {% if messages %}
            {% for category, message in messages %}
                <div class="flash {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        
        <h2>Formulaire avec token CSRF</h2>
        <form method="POST" action="/test-csrf">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <div class="form-group">
                <label for="name">Nom:</label>
                <input type="text" id="name" name="name" value="Test">
            </div>
            <button type="submit" class="btn">Soumettre avec CSRF</button>
        </form>
        
        <h2>Formulaire sans token CSRF</h2>
        <form method="POST" action="/test-csrf-no-token">
            <div class="form-group">
                <label for="name_no_token">Nom:</label>
                <input type="text" id="name_no_token" name="name" value="Test">
            </div>
            <button type="submit" class="btn">Soumettre sans CSRF</button>
        </form>
        
        <div class="debug-info">
            <h3>Informations de débogage</h3>
            <p><strong>Session contient CSRF token:</strong> {{ 'csrf_token' in session }}</p>
            <p><strong>Cookie de session présent:</strong> {{ 'session' in request.cookies }}</p>
            <p><strong>CSRF token généré:</strong> {{ csrf_token() }}</p>
            <h4>Cookies:</h4>
            <pre>{{ cookies }}</pre>
            <h4>Headers:</h4>
            <pre>{{ headers }}</pre>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Page d'accueil avec formulaire de test"""
    logger.debug("Affichage de la page d'accueil")
    logger.debug(f"Session: {dict(session)}")
    logger.debug(f"Cookies: {request.cookies}")
    
    # Générer un token CSRF pour s'assurer qu'il est dans la session
    csrf_token = generate_csrf()
    logger.debug(f"Token CSRF généré: {csrf_token}")
    
    return render_template_string(
        form_template, 
        messages=[], 
        cookies=dict(request.cookies),
        headers=dict(request.headers)
    )

@app.route('/test-csrf', methods=['POST'])
def test_csrf():
    """Route pour tester un formulaire avec protection CSRF"""
    logger.debug("=== TEST CSRF AVEC TOKEN ===")
    logger.debug(f"Méthode: {request.method}")
    logger.debug(f"Form data: {dict(request.form)}")
    logger.debug(f"CSRF token présent dans le formulaire: {'csrf_token' in request.form}")
    logger.debug(f"Session: {dict(session)}")
    
    name = request.form.get('name', '')
    flash(f'Formulaire avec CSRF soumis avec succès! Nom: {name}', 'success')
    return redirect(url_for('index'))

@app.route('/test-csrf-no-token', methods=['POST'])
def test_csrf_no_token():
    """Route pour tester un formulaire sans protection CSRF"""
    # Cette route devrait normalement échouer avec une erreur CSRF
    # mais nous la capturons pour des besoins de diagnostic
    try:
        logger.debug("=== TEST CSRF SANS TOKEN ===")
        logger.debug(f"Méthode: {request.method}")
        logger.debug(f"Form data: {dict(request.form)}")
        logger.debug(f"Session: {dict(session)}")
        
        name = request.form.get('name', '')
        flash(f'Formulaire sans CSRF soumis avec succès! Nom: {name}', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Erreur lors de la soumission sans CSRF: {str(e)}")
        flash(f'Erreur CSRF: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    logger.info("Démarrage de l'application de diagnostic CSRF")
    app.run(port=5001, debug=True)
