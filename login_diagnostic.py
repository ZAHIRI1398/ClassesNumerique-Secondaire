from flask import Flask, render_template_string, request, flash, redirect, url_for, session
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
import logging
import requests
import json

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('login_diagnostic.log')]
)
logger = logging.getLogger('login_diagnostic')

# Création de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'diagnostic-secret-key'
app.config['DEBUG'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialisation de la protection CSRF
csrf = CSRFProtect(app)

# Template HTML pour le formulaire de test
form_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Diagnostic de Connexion</title>
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
        <h1>Diagnostic de Connexion</h1>
        
        {% if messages %}
            {% for category, message in messages %}
                <div class="flash {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        
        <h2>Formulaire de connexion (simulation)</h2>
        <form method="POST" action="/test-login">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" value="test@example.com">
            </div>
            <div class="form-group">
                <label for="password">Mot de passe:</label>
                <input type="password" id="password" name="password" value="password123">
            </div>
            <div class="form-group">
                <input type="checkbox" id="remember_me" name="remember_me" value="1">
                <label for="remember_me">Se souvenir de moi</label>
            </div>
            <button type="submit" class="btn">Se connecter</button>
        </form>
        
        <h2>Test de l'API de connexion</h2>
        <form method="POST" action="/test-api-login">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <div class="form-group">
                <label for="api_url">URL de l'API:</label>
                <input type="text" id="api_url" name="api_url" value="http://localhost:5000/login" style="width: 100%;">
            </div>
            <div class="form-group">
                <label for="api_email">Email:</label>
                <input type="email" id="api_email" name="api_email" value="test@example.com">
            </div>
            <div class="form-group">
                <label for="api_password">Mot de passe:</label>
                <input type="password" id="api_password" name="api_password" value="password123">
            </div>
            <button type="submit" class="btn">Tester API</button>
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
            <h4>Résultat du test API:</h4>
            <pre>{{ api_result }}</pre>
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
        headers=dict(request.headers),
        api_result="Pas encore testé"
    )

@app.route('/test-login', methods=['POST'])
def test_login():
    """Route pour tester un formulaire de connexion"""
    logger.debug("=== TEST LOGIN ===")
    logger.debug(f"Méthode: {request.method}")
    logger.debug(f"Form data: {dict(request.form)}")
    logger.debug(f"CSRF token présent dans le formulaire: {'csrf_token' in request.form}")
    logger.debug(f"Session: {dict(session)}")
    
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    remember_me = request.form.get('remember_me') == '1'
    
    logger.debug(f"Email: {email}, Password: {'*' * len(password)}, Remember me: {remember_me}")
    flash(f'Formulaire de connexion soumis avec succès! Email: {email}, Remember me: {remember_me}', 'success')
    return redirect(url_for('index'))

@app.route('/test-api-login', methods=['POST'])
def test_api_login():
    """Route pour tester l'API de connexion"""
    logger.debug("=== TEST API LOGIN ===")
    
    api_url = request.form.get('api_url', '')
    email = request.form.get('api_email', '')
    password = request.form.get('api_password', '')
    
    logger.debug(f"API URL: {api_url}")
    logger.debug(f"Email: {email}, Password: {'*' * len(password)}")
    
    result = "Pas de résultat"
    try:
        # Récupérer le CSRF token de la page cible
        session_response = requests.get(api_url)
        cookies = session_response.cookies
        
        # Extraire le CSRF token (peut varier selon l'implémentation)
        csrf_token = None
        for cookie in cookies:
            if cookie.name == 'csrf_token':
                csrf_token = cookie.value
                break
        
        logger.debug(f"Cookies récupérés: {cookies}")
        logger.debug(f"CSRF token récupéré: {csrf_token}")
        
        # Faire la requête de connexion
        login_data = {
            'email': email,
            'password': password,
            'remember_me': '1',
            'csrf_token': csrf_token
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrf_token if csrf_token else ''
        }
        
        response = requests.post(
            api_url,
            data=login_data,
            cookies=cookies,
            headers=headers,
            allow_redirects=False
        )
        
        logger.debug(f"Status code: {response.status_code}")
        logger.debug(f"Headers: {response.headers}")
        
        if 300 <= response.status_code < 400:
            result = f"Redirection vers: {response.headers.get('Location', 'Inconnu')}"
        else:
            result = f"Réponse: {response.text[:500]}..."
        
        flash(f'Test API effectué. Status: {response.status_code}', 'success')
    except Exception as e:
        logger.error(f"Erreur lors du test API: {str(e)}")
        result = f"Erreur: {str(e)}"
        flash(f'Erreur lors du test API: {str(e)}', 'error')
    
    return render_template_string(
        form_template,
        messages=[(category, message) for category, message in session.get('_flashes', [])],
        cookies=dict(request.cookies),
        headers=dict(request.headers),
        api_result=result
    )

if __name__ == '__main__':
    logger.info("Démarrage de l'application de diagnostic de connexion")
    app.run(port=5002, debug=True)
