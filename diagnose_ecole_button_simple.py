"""
Script de diagnostic pour vérifier pourquoi le bouton École ne s'affiche pas dans l'interface
"""
import os
import sys
import logging
from flask import Flask, render_template, url_for
from jinja2 import Environment, FileSystemLoader

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("diagnose_ecole_button.log", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_template_content():
    """Vérifie le contenu du template login.html"""
    template_path = os.path.join('templates', 'login.html')
    
    if not os.path.exists(template_path):
        logger.error(f"ERREUR: Le template {template_path} n'existe pas!")
        return False
    
    logger.info(f"OK: Le template {template_path} existe.")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Vérifier la présence du bouton École dans le modal de connexion
        login_modal_ecole = 'url_for(\'register_school\')' in content and 'École' in content and 'fa-school' in content
        if login_modal_ecole:
            logger.info("OK: Le code du bouton École est présent dans le template.")
            
            # Trouver les occurrences du bouton École
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'url_for(\'register_school\')' in line or 'fa-school' in line:
                    logger.info(f"Ligne {i+1}: {line.strip()}")
        else:
            logger.error("ERREUR: Le code du bouton École n'est pas présent dans le template!")
            return False
    
    return True

def check_route_exists():
    """Vérifie si la route register_school existe dans app.py"""
    if not os.path.exists('app.py'):
        logger.error("ERREUR: Le fichier app.py n'existe pas!")
        return False
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        if "@app.route('/register/school'" in content and "def register_school():" in content:
            logger.info("OK: La route register_school est définie dans app.py")
            return True
        else:
            logger.error("ERREUR: La route register_school n'est pas définie dans app.py!")
            return False

def test_template_rendering():
    """Teste le rendu du template avec Jinja2 pour voir si le bouton École est rendu"""
    try:
        # Créer un environnement Jinja2 pour tester le rendu du template
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('login.html')
        
        # Simuler la fonction url_for de Flask
        def mock_url_for(endpoint, **kwargs):
            if endpoint == 'register_school':
                return '/register/school'
            elif endpoint == 'register_teacher':
                return '/register/teacher'
            elif endpoint == 'register_student':
                return '/register/student'
            elif endpoint == 'login':
                return '/login'
            else:
                return f'/{endpoint}'
        
        # Contexte minimal pour le rendu
        context = {
            'url_for': mock_url_for,
            'get_flashed_messages': lambda: [],
            'csrf_token': lambda: 'mock-csrf-token'
        }
        
        # Rendre le template
        rendered = template.render(**context)
        
        # Vérifier si le bouton École est présent dans le rendu
        if '/register/school' in rendered and 'École' in rendered and 'fa-school' in rendered:
            logger.info("OK: Le bouton École est présent dans le rendu du template.")
            return True
        else:
            logger.error("ERREUR: Le bouton École n'est pas présent dans le rendu du template!")
            return False
    except Exception as e:
        logger.error(f"ERREUR: Erreur lors du rendu du template: {str(e)}")
        return False

def check_flask_config():
    """Vérifie la configuration Flask pour s'assurer que les templates sont chargés correctement"""
    try:
        # Créer une application Flask minimale pour tester
        app = Flask(__name__, template_folder='templates')
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-key'
        
        # Ajouter une route de test
        @app.route('/test')
        def test():
            return render_template('login.html')
        
        # Vérifier si le template est trouvé
        with app.test_request_context():
            try:
                url = url_for('register_school')
                logger.info(f"OK: L'URL pour register_school est: {url}")
            except Exception as e:
                logger.error(f"ERREUR: Erreur lors de la génération de l'URL pour register_school: {str(e)}")
                return False
        
        logger.info("OK: La configuration Flask semble correcte.")
        return True
    except Exception as e:
        logger.error(f"ERREUR: Erreur lors de la vérification de la configuration Flask: {str(e)}")
        return False

def check_browser_compatibility():
    """Vérifie les potentiels problèmes de compatibilité navigateur"""
    logger.info("INFO: Vérification de la compatibilité navigateur:")
    logger.info("  - Assurez-vous que JavaScript est activé dans votre navigateur")
    logger.info("  - Essayez de vider le cache du navigateur (Ctrl+F5 ou Cmd+Shift+R)")
    logger.info("  - Testez avec un autre navigateur (Chrome, Firefox, Edge)")
    return True

def main():
    """Fonction principale de diagnostic"""
    logger.info("=== DÉBUT DU DIAGNOSTIC DU BOUTON ÉCOLE ===")
    
    # Vérifier le contenu du template
    template_ok = check_template_content()
    
    # Vérifier si la route existe
    route_ok = check_route_exists()
    
    # Tester le rendu du template
    rendering_ok = test_template_rendering()
    
    # Vérifier la configuration Flask
    flask_ok = check_flask_config()
    
    # Vérifier la compatibilité navigateur
    browser_ok = check_browser_compatibility()
    
    # Résumé
    logger.info("\n=== RÉSUMÉ DU DIAGNOSTIC ===")
    logger.info(f"Template login.html: {'OK' if template_ok else 'PROBLÈME'}")
    logger.info(f"Route register_school: {'OK' if route_ok else 'PROBLÈME'}")
    logger.info(f"Rendu du template: {'OK' if rendering_ok else 'PROBLÈME'}")
    logger.info(f"Configuration Flask: {'OK' if flask_ok else 'PROBLÈME'}")
    
    if template_ok and route_ok and rendering_ok and flask_ok:
        logger.info("\nTous les tests ont réussi. Le problème est probablement lié au navigateur ou au déploiement.")
        logger.info("Recommandations:")
        logger.info("1. Videz le cache du navigateur")
        logger.info("2. Redémarrez le serveur Flask")
        logger.info("3. Vérifiez que les modifications ont été déployées")
        logger.info("4. Inspectez le DOM dans les outils de développement du navigateur")
    else:
        logger.info("\nCertains tests ont échoué. Veuillez corriger les problèmes identifiés.")
    
    logger.info("=== FIN DU DIAGNOSTIC DU BOUTON ÉCOLE ===")

if __name__ == "__main__":
    main()
    print("Diagnostic terminé. Consultez le fichier diagnose_ecole_button.log pour les résultats détaillés.")
