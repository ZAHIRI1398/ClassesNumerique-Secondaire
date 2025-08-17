from flask import Flask, render_template, current_app
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('payment_templates_check.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

app = Flask(__name__, 
            template_folder='production_code/ClassesNumerique-Secondaire-main/templates')

@app.route('/check-templates')
def check_templates():
    results = []
    
    # Vérifier si le dossier payment existe
    payment_dir = os.path.join(app.template_folder, 'payment')
    payment_dir_exists = os.path.exists(payment_dir)
    results.append(f"Dossier payment existe: {payment_dir_exists}")
    logger.info(f"Dossier payment existe: {payment_dir_exists}")
    
    if payment_dir_exists:
        # Lister les fichiers dans le dossier payment
        payment_files = os.listdir(payment_dir)
        results.append(f"Fichiers dans payment/: {payment_files}")
        logger.info(f"Fichiers dans payment/: {payment_files}")
        
        # Vérifier chaque template
        templates_to_check = [
            'select_school.html',
            'subscribe.html',
            'success.html',
            'cancel.html',
            'simulate_checkout.html'
        ]
        
        for template in templates_to_check:
            template_path = os.path.join(payment_dir, template)
            template_exists = os.path.exists(template_path)
            results.append(f"Template {template} existe: {template_exists}")
            logger.info(f"Template {template} existe: {template_exists}")
            
            if template_exists:
                # Vérifier si le template est accessible via Flask
                try:
                    rendered = render_template(f"payment/{template}")
                    results.append(f"Template {template} rendu avec succès")
                    logger.info(f"Template {template} rendu avec succès")
                except Exception as e:
                    results.append(f"Erreur lors du rendu de {template}: {str(e)}")
                    logger.error(f"Erreur lors du rendu de {template}: {str(e)}")
    
    # Vérifier la structure des dossiers
    results.append(f"Structure des dossiers:")
    for root, dirs, files in os.walk(app.template_folder):
        rel_path = os.path.relpath(root, app.template_folder)
        if rel_path == '.':
            rel_path = ''
        results.append(f"Dossier: {rel_path}")
        logger.info(f"Dossier: {rel_path}")
        for file in files:
            if file.endswith('.html'):
                results.append(f"  - {file}")
                logger.info(f"  - {file}")
    
    return "<br>".join(results)

@app.route('/debug-payment-route')
def debug_payment_route():
    try:
        # Simuler le rendu du template select_school.html avec des données fictives
        schools = [('École Test', 1)]
        rendered = render_template('payment/select_school.html', schools=schools)
        return "Template rendu avec succès:<br>" + rendered
    except Exception as e:
        logger.error(f"Erreur lors du rendu: {str(e)}")
        return f"Erreur lors du rendu: {str(e)}"

if __name__ == '__main__':
    logger.info("Démarrage de l'application de diagnostic")
    app.run(debug=True, port=5001)
