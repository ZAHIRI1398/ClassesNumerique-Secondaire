"""
Script de diagnostic pour identifier les problèmes de redirection entre
l'inscription d'école et le système d'abonnement.
"""
import os
import sys
from flask import Flask, url_for
from flask_login import LoginManager, current_user
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('payment_diagnosis.log')
    ]
)
logger = logging.getLogger(__name__)

# Création d'une mini-application Flask pour les tests
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle_secrete_pour_diagnostic'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/classe_numerique.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Import des modèles et routes nécessaires
try:
    from models import db, User, School
    db.init_app(app)
    logger.info("✅ Modèles importés avec succès")
except Exception as e:
    logger.error(f"❌ Erreur lors de l'importation des modèles: {str(e)}")
    sys.exit(1)

try:
    from payment_routes import payment_bp
    app.register_blueprint(payment_bp)
    logger.info("✅ Blueprint de paiement enregistré avec succès")
except Exception as e:
    logger.error(f"❌ Erreur lors de l'enregistrement du blueprint de paiement: {str(e)}")
    sys.exit(1)

# Fonction pour tester les URLs
def test_url(url_name, **kwargs):
    try:
        with app.test_request_context():
            url = url_for(url_name, **kwargs)
            logger.info(f"✅ URL '{url_name}' générée avec succès: {url}")
            return url
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération de l'URL '{url_name}': {str(e)}")
        return None

def main():
    """Fonction principale de diagnostic"""
    logger.info("=== DÉBUT DU DIAGNOSTIC DU SYSTÈME DE PAIEMENT ===")
    
    # 1. Vérifier les routes de paiement
    logger.info("\n1. VÉRIFICATION DES ROUTES DE PAIEMENT")
    payment_routes = [
        ('payment.subscribe', {'subscription_type': 'school'}),
        ('payment.select_school', {}),
        ('payment.join_school', {})
    ]
    
    for route_name, kwargs in payment_routes:
        test_url(route_name, **kwargs)
    
    # 2. Vérifier le template select_school.html
    logger.info("\n2. VÉRIFICATION DU TEMPLATE SELECT_SCHOOL.HTML")
    template_path = os.path.join('templates', 'payment', 'select_school.html')
    if os.path.exists(template_path):
        logger.info(f"✅ Template {template_path} existe")
        
        # Vérifier le contenu du template
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'Souscrire un nouvel abonnement école' in content:
                logger.info("✅ Bouton 'Souscrire un nouvel abonnement école' trouvé dans le template")
                
                # Vérifier l'URL du bouton
                if "url_for('payment.subscribe', subscription_type='school')" in content:
                    logger.info("✅ URL correcte pour le bouton d'abonnement")
                else:
                    logger.error("❌ URL incorrecte pour le bouton d'abonnement")
            else:
                logger.error("❌ Bouton 'Souscrire un nouvel abonnement école' non trouvé dans le template")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la lecture du template: {str(e)}")
    else:
        logger.error(f"❌ Template {template_path} n'existe pas")
    
    # 3. Vérifier la route subscribe
    logger.info("\n3. VÉRIFICATION DE LA ROUTE SUBSCRIBE")
    try:
        with app.test_request_context():
            # Simuler une requête à la route subscribe
            url = url_for('payment.subscribe', subscription_type='school')
            logger.info(f"URL de souscription: {url}")
            
            # Vérifier si la route est correctement définie dans payment_routes.py
            if hasattr(payment_bp.view_functions, 'subscribe'):
                logger.info("✅ Fonction 'subscribe' trouvée dans le blueprint de paiement")
            else:
                logger.error("❌ Fonction 'subscribe' non trouvée dans le blueprint de paiement")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification de la route subscribe: {str(e)}")
    
    # 4. Vérifier l'intégration avec le module d'inscription d'école
    logger.info("\n4. VÉRIFICATION DE L'INTÉGRATION AVEC LE MODULE D'INSCRIPTION D'ÉCOLE")
    try:
        from integrate_school_registration_mod import integrate_school_registration_mod
        logger.info("✅ Module d'inscription d'école importé avec succès")
        
        # Vérifier si le module est correctement intégré dans app.py
        # (Cette vérification est limitée car nous ne pouvons pas accéder à l'app principale)
        logger.info("ℹ️ Pour vérifier l'intégration complète, consultez app.py ligne ~70")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'importation du module d'inscription d'école: {str(e)}")
    
    logger.info("\n=== FIN DU DIAGNOSTIC DU SYSTÈME DE PAIEMENT ===")
    logger.info("\nConsultez le fichier payment_diagnosis.log pour plus de détails.")
    
    print("\n=== RÉSUMÉ DU DIAGNOSTIC ===")
    print("Un rapport détaillé a été généré dans payment_diagnosis.log")
    print("Pour résoudre le problème:")
    print("1. Vérifiez que le bouton 'Souscrire un nouvel abonnement école' pointe vers la bonne URL")
    print("2. Assurez-vous que la route payment.subscribe est correctement définie")
    print("3. Vérifiez l'intégration entre le module d'inscription d'école et le système de paiement")
    print("4. Consultez les logs de l'application pour détecter d'éventuelles erreurs JavaScript")

if __name__ == "__main__":
    main()
