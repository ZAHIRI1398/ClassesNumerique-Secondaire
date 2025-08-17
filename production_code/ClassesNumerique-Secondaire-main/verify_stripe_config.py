import os
import sys
import logging
from datetime import datetime
import stripe
from flask import Flask

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"verify_stripe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask pour accéder aux variables d'environnement
app = Flask(__name__)

def verify_stripe_configuration():
    """Vérifier la configuration de Stripe en production"""
    try:
        logger.info("=== VÉRIFICATION DE LA CONFIGURATION STRIPE ===")
        
        # 1. Vérifier les clés Stripe
        stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
        stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        stripe_webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        if not stripe_secret_key:
            logger.warning("STRIPE_SECRET_KEY n'est pas définie. Le mode simulation sera utilisé.")
        else:
            # Masquer la clé pour la sécurité
            masked_key = f"{stripe_secret_key[:4]}...{stripe_secret_key[-4:]}" if len(stripe_secret_key) > 8 else "***"
            logger.info(f"STRIPE_SECRET_KEY est définie: {masked_key}")
            
            # Tester la connexion à l'API Stripe
            try:
                stripe.api_key = stripe_secret_key
                account = stripe.Account.retrieve()
                logger.info(f"Connexion à l'API Stripe réussie. Compte: {account.get('email', 'Non disponible')}")
            except Exception as e:
                logger.error(f"Erreur lors de la connexion à l'API Stripe: {str(e)}")
        
        if not stripe_publishable_key:
            logger.warning("STRIPE_PUBLISHABLE_KEY n'est pas définie. Cela peut causer des problèmes avec le widget de paiement.")
        else:
            masked_key = f"{stripe_publishable_key[:4]}...{stripe_publishable_key[-4:]}" if len(stripe_publishable_key) > 8 else "***"
            logger.info(f"STRIPE_PUBLISHABLE_KEY est définie: {masked_key}")
        
        if not stripe_webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET n'est pas définie. Les webhooks Stripe ne fonctionneront pas correctement.")
        else:
            logger.info("STRIPE_WEBHOOK_SECRET est définie.")
        
        # 2. Vérifier les URLs de callback
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        success_url = f"{base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/payment/cancel"
        
        logger.info(f"URL de succès: {success_url}")
        logger.info(f"URL d'annulation: {cancel_url}")
        
        # 3. Vérifier les prix configurés
        teacher_price = os.environ.get('TEACHER_SUBSCRIPTION_PRICE', '4000')
        school_price = os.environ.get('SCHOOL_SUBSCRIPTION_PRICE', '8000')
        
        logger.info(f"Prix abonnement enseignant: {int(teacher_price)/100}€")
        logger.info(f"Prix abonnement école: {int(school_price)/100}€")
        
        # 4. Vérifier le mode de fonctionnement
        if not stripe_secret_key:
            logger.warning("Le système fonctionne en MODE SIMULATION. Les paiements ne seront pas réels.")
            logger.info("Pour activer les paiements réels, définissez STRIPE_SECRET_KEY dans les variables d'environnement.")
        else:
            if stripe_secret_key.startswith('sk_test_'):
                logger.warning("Le système utilise une clé Stripe de TEST. Les paiements seront simulés.")
            elif stripe_secret_key.startswith('sk_live_'):
                logger.info("Le système utilise une clé Stripe de PRODUCTION. Les paiements seront réels.")
            else:
                logger.warning(f"Format de clé Stripe inconnu: {stripe_secret_key[:7]}...")
        
        logger.info("=== VÉRIFICATION TERMINÉE ===")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la configuration Stripe: {str(e)}")

if __name__ == "__main__":
    verify_stripe_configuration()
