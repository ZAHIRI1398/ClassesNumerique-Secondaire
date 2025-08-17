#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnostic et correction des problèmes de connexion et CSRF
Ce script analyse et corrige les problèmes de connexion et de gestion CSRF
dans l'application Flask ClassesNumerique-Secondaire.
"""

import os
import sys
import logging
import requests
from flask import Flask, render_template_string, request, session, redirect, url_for
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fix_login_csrf.log')
    ]
)
logger = logging.getLogger('fix_login_csrf')

def test_csrf_protection():
    """Teste la protection CSRF avec le script csrf_diagnostic.py"""
    logger.info("Test de la protection CSRF...")
    try:
        # Vérifier si le script existe
        if not os.path.exists('csrf_diagnostic.py'):
            logger.error("Le script csrf_diagnostic.py n'existe pas!")
            return False
        
        # Exécuter le script dans un processus séparé
        import subprocess
        process = subprocess.Popen(
            [sys.executable, 'csrf_diagnostic.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Attendre que le serveur démarre
        import time
        time.sleep(2)
        
        # Tester la protection CSRF
        try:
            # Test avec token CSRF
            session_response = requests.get('http://localhost:5001/')
            cookies = session_response.cookies
            
            # Extraire le CSRF token
            csrf_token = None
            for cookie in cookies:
                if cookie.name == 'csrf_token':
                    csrf_token = cookie.value
                    break
            
            # Test avec token CSRF
            response_with_token = requests.post(
                'http://localhost:5001/test-csrf',
                data={'name': 'Test', 'csrf_token': csrf_token},
                cookies=cookies
            )
            
            # Test sans token CSRF
            response_without_token = requests.post(
                'http://localhost:5001/test-csrf-no-token',
                data={'name': 'Test'},
                cookies=cookies
            )
            
            logger.info(f"Test avec token CSRF: {response_with_token.status_code}")
            logger.info(f"Test sans token CSRF: {response_without_token.status_code}")
            
            # Vérifier que la protection CSRF fonctionne
            csrf_protection_works = (
                response_with_token.status_code == 200 and
                response_without_token.status_code != 200
            )
            
            logger.info(f"Protection CSRF fonctionne: {csrf_protection_works}")
            return csrf_protection_works
        
        except Exception as e:
            logger.error(f"Erreur lors du test CSRF: {str(e)}")
            return False
        finally:
            # Arrêter le serveur
            process.terminate()
            
    except Exception as e:
        logger.error(f"Erreur lors du test de protection CSRF: {str(e)}")
        return False

def test_login_form_submission():
    """Teste la soumission du formulaire de connexion avec login_diagnostic.py"""
    logger.info("Test de la soumission du formulaire de connexion...")
    try:
        # Vérifier si le script existe
        if not os.path.exists('login_diagnostic.py'):
            logger.error("Le script login_diagnostic.py n'existe pas!")
            return False
        
        # Exécuter le script dans un processus séparé
        import subprocess
        process = subprocess.Popen(
            [sys.executable, 'login_diagnostic.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Attendre que le serveur démarre
        import time
        time.sleep(2)
        
        # Tester la soumission du formulaire
        try:
            # Récupérer la page avec le formulaire
            session_response = requests.get('http://localhost:5002/')
            cookies = session_response.cookies
            
            # Extraire le CSRF token
            csrf_token = None
            for cookie in cookies:
                if cookie.name == 'csrf_token':
                    csrf_token = cookie.value
                    break
            
            # Soumettre le formulaire
            response = requests.post(
                'http://localhost:5002/test-login',
                data={
                    'email': 'test@example.com',
                    'password': 'password123',
                    'remember_me': '1',
                    'csrf_token': csrf_token
                },
                cookies=cookies
            )
            
            logger.info(f"Soumission du formulaire: {response.status_code}")
            
            # Vérifier que la soumission fonctionne
            form_submission_works = response.status_code == 200
            
            logger.info(f"Soumission du formulaire fonctionne: {form_submission_works}")
            return form_submission_works
        
        except Exception as e:
            logger.error(f"Erreur lors du test de soumission: {str(e)}")
            return False
        finally:
            # Arrêter le serveur
            process.terminate()
            
    except Exception as e:
        logger.error(f"Erreur lors du test de soumission du formulaire: {str(e)}")
        return False

def check_app_initialization():
    """Vérifie l'ordre d'initialisation dans app.py"""
    logger.info("Vérification de l'ordre d'initialisation dans app.py...")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifier l'ordre d'initialisation
        app_creation_index = content.find('app = Flask(__name__)')
        config_loading_index = content.find('app.config.from_object')
        extensions_init_index = content.find('init_extensions(app)')
        
        # Vérifier que l'ordre est correct
        correct_order = (
            app_creation_index < config_loading_index < extensions_init_index
        )
        
        # Vérifier les initialisations multiples
        multiple_config_loading = content.count('app.config.from_object') > 1
        multiple_extensions_init = content.count('init_extensions(app)') > 1
        
        logger.info(f"Ordre d'initialisation correct: {correct_order}")
        logger.info(f"Chargement multiple de la configuration: {multiple_config_loading}")
        logger.info(f"Initialisation multiple des extensions: {multiple_extensions_init}")
        
        return {
            'correct_order': correct_order,
            'multiple_config_loading': multiple_config_loading,
            'multiple_extensions_init': multiple_extensions_init
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'initialisation: {str(e)}")
        return {
            'correct_order': False,
            'multiple_config_loading': True,
            'multiple_extensions_init': True
        }

def check_session_cookie_config():
    """Vérifie la configuration des cookies de session"""
    logger.info("Vérification de la configuration des cookies de session...")
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifier les paramètres des cookies de session
        dev_secure = 'SESSION_COOKIE_SECURE = False' in content
        dev_httponly = 'SESSION_COOKIE_HTTPONLY = True' in content
        dev_samesite = "SESSION_COOKIE_SAMESITE = 'Lax'" in content
        
        prod_secure = 'SESSION_COOKIE_SECURE = True' in content
        prod_httponly = 'SESSION_COOKIE_HTTPONLY = True' in content
        prod_samesite = "SESSION_COOKIE_SAMESITE = 'Lax'" in content
        
        logger.info(f"Développement - SESSION_COOKIE_SECURE = False: {dev_secure}")
        logger.info(f"Développement - SESSION_COOKIE_HTTPONLY = True: {dev_httponly}")
        logger.info(f"Développement - SESSION_COOKIE_SAMESITE = 'Lax': {dev_samesite}")
        
        logger.info(f"Production - SESSION_COOKIE_SECURE = True: {prod_secure}")
        logger.info(f"Production - SESSION_COOKIE_HTTPONLY = True: {prod_httponly}")
        logger.info(f"Production - SESSION_COOKIE_SAMESITE = 'Lax': {prod_samesite}")
        
        return {
            'dev_config_ok': dev_secure and dev_httponly and dev_samesite,
            'prod_config_ok': prod_secure and prod_httponly and prod_samesite
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la configuration des cookies: {str(e)}")
        return {
            'dev_config_ok': False,
            'prod_config_ok': False
        }

def fix_app_initialization():
    """Corrige l'ordre d'initialisation dans app.py si nécessaire"""
    logger.info("Correction de l'ordre d'initialisation dans app.py...")
    try:
        # Vérifier l'ordre d'initialisation actuel
        init_check = check_app_initialization()
        
        if init_check['correct_order'] and not init_check['multiple_config_loading'] and not init_check['multiple_extensions_init']:
            logger.info("L'ordre d'initialisation est déjà correct!")
            return True
        
        # Sauvegarder le fichier original
        import shutil
        backup_file = 'app.py.bak.fix_login_csrf'
        shutil.copy2('app.py', backup_file)
        logger.info(f"Sauvegarde de app.py dans {backup_file}")
        
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        # Identifier les sections importantes
        app_creation_line = -1
        config_loading_lines = []
        extensions_init_lines = []
        
        for i, line in enumerate(content):
            if 'app = Flask(__name__)' in line:
                app_creation_line = i
            if 'app.config.from_object' in line:
                config_loading_lines.append(i)
            if 'init_extensions(app)' in line:
                extensions_init_lines.append(i)
        
        # Si l'ordre est incorrect ou il y a des initialisations multiples
        if len(config_loading_lines) > 1 or len(extensions_init_lines) > 1:
            # Garder seulement la première occurrence de chaque initialisation
            if len(config_loading_lines) > 1:
                for line in config_loading_lines[1:]:
                    content[line] = '# ' + content[line]  # Commenter les lignes redondantes
            
            if len(extensions_init_lines) > 1:
                for line in extensions_init_lines[1:]:
                    content[line] = '# ' + content[line]  # Commenter les lignes redondantes
            
            # Écrire le fichier modifié
            with open('app.py', 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            logger.info("Correction des initialisations multiples effectuée!")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Erreur lors de la correction de l'initialisation: {str(e)}")
        return False

def create_test_app():
    """Crée une application Flask de test pour vérifier la configuration des cookies de session"""
    logger.info("Création d'une application Flask de test...")
    
    # Template HTML pour le test
    test_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test de Configuration des Cookies</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .success { color: green; }
            .error { color: red; }
            .debug-info { background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; margin-top: 20px; }
            pre { white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Test de Configuration des Cookies</h1>
            
            <h2>Résultats</h2>
            <ul>
                <li>Cookie de session présent: <span class="{{ 'success' if session_cookie_present else 'error' }}">{{ session_cookie_present }}</span></li>
                <li>CSRF token présent: <span class="{{ 'success' if csrf_token_present else 'error' }}">{{ csrf_token_present }}</span></li>
                <li>Cookie Secure: <span class="{{ 'success' if cookie_secure == expected_secure else 'error' }}">{{ cookie_secure }} (attendu: {{ expected_secure }})</span></li>
                <li>Cookie HttpOnly: <span class="{{ 'success' if cookie_httponly else 'error' }}">{{ cookie_httponly }}</span></li>
                <li>Cookie SameSite: <span class="{{ 'success' if cookie_samesite == 'Lax' else 'error' }}">{{ cookie_samesite }}</span></li>
            </ul>
            
            <h2>Actions</h2>
            <form method="POST" action="/test-cookie">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <button type="submit">Tester les cookies</button>
            </form>
            
            <div class="debug-info">
                <h3>Informations de débogage</h3>
                <h4>Cookies:</h4>
                <pre>{{ cookies }}</pre>
                <h4>Headers:</h4>
                <pre>{{ headers }}</pre>
                <h4>Session:</h4>
                <pre>{{ session_data }}</pre>
                <h4>Configuration:</h4>
                <pre>{{ config }}</pre>
            </div>
        </div>
    </body>
    </html>
    '''
    
    # Créer l'application Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['DEBUG'] = True
    
    # Configurer les cookies de session selon l'environnement
    is_https = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_SECURE'] = is_https
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialiser la protection CSRF
    csrf = CSRFProtect(app)
    
    @app.route('/')
    def index():
        # Générer un token CSRF
        csrf_token = generate_csrf()
        
        # Vérifier les cookies
        session_cookie_present = 'session' in request.cookies
        csrf_token_present = 'csrf_token' in request.cookies
        
        # Récupérer les attributs des cookies
        cookie_secure = request.cookies.get('session', {}).get('secure', False)
        cookie_httponly = request.cookies.get('session', {}).get('httponly', False)
        cookie_samesite = request.cookies.get('session', {}).get('samesite', 'None')
        
        return render_template_string(
            test_template,
            session_cookie_present=session_cookie_present,
            csrf_token_present=csrf_token_present,
            cookie_secure=cookie_secure,
            expected_secure=is_https,
            cookie_httponly=cookie_httponly,
            cookie_samesite=cookie_samesite,
            cookies=dict(request.cookies),
            headers=dict(request.headers),
            session_data=dict(session),
            config=app.config
        )
    
    @app.route('/test-cookie', methods=['POST'])
    def test_cookie():
        # Ajouter des données à la session
        session['test'] = 'value'
        return redirect(url_for('index'))
    
    return app

def main():
    """Fonction principale"""
    logger.info("Démarrage du script de diagnostic et correction...")
    
    # Vérifier l'ordre d'initialisation
    init_check = check_app_initialization()
    if not init_check['correct_order'] or init_check['multiple_config_loading'] or init_check['multiple_extensions_init']:
        logger.warning("Problèmes détectés dans l'ordre d'initialisation!")
        fix_app_initialization()
    else:
        logger.info("L'ordre d'initialisation est correct.")
    
    # Vérifier la configuration des cookies de session
    cookie_check = check_session_cookie_config()
    if not cookie_check['dev_config_ok'] or not cookie_check['prod_config_ok']:
        logger.warning("Problèmes détectés dans la configuration des cookies de session!")
    else:
        logger.info("La configuration des cookies de session est correcte.")
    
    # Tester la protection CSRF
    csrf_works = test_csrf_protection()
    if not csrf_works:
        logger.warning("La protection CSRF ne fonctionne pas correctement!")
    else:
        logger.info("La protection CSRF fonctionne correctement.")
    
    # Tester la soumission du formulaire
    form_works = test_login_form_submission()
    if not form_works:
        logger.warning("La soumission du formulaire ne fonctionne pas correctement!")
    else:
        logger.info("La soumission du formulaire fonctionne correctement.")
    
    # Résumé des résultats
    logger.info("=== RÉSUMÉ DES RÉSULTATS ===")
    logger.info(f"Ordre d'initialisation correct: {init_check['correct_order']}")
    logger.info(f"Configuration des cookies de session correcte: {cookie_check['dev_config_ok'] and cookie_check['prod_config_ok']}")
    logger.info(f"Protection CSRF fonctionnelle: {csrf_works}")
    logger.info(f"Soumission du formulaire fonctionnelle: {form_works}")
    
    # Recommandations
    logger.info("=== RECOMMANDATIONS ===")
    if not init_check['correct_order'] or init_check['multiple_config_loading'] or init_check['multiple_extensions_init']:
        logger.info("1. Corriger l'ordre d'initialisation dans app.py")
    if not cookie_check['dev_config_ok'] or not cookie_check['prod_config_ok']:
        logger.info("2. Corriger la configuration des cookies de session dans config.py")
    if not csrf_works:
        logger.info("3. Vérifier l'initialisation de la protection CSRF")
    if not form_works:
        logger.info("4. Vérifier la soumission du formulaire de connexion")

if __name__ == '__main__':
    main()
