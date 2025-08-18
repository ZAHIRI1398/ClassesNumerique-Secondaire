"""
Script de vérification de la correction du paiement pour les enseignants sans école.
Ce script teste la route de paiement pour s'assurer qu'elle fonctionne correctement.
"""

import requests
import sys
import os
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'verify_payment_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_payment_route():
    """Teste la route de création de session de paiement"""
    try:
        # URL de l'application en production
        base_url = "https://web-production-9ad7.up.railway.app"
        
        # Endpoint pour la création de session de paiement
        endpoint = f"{base_url}/payment/create-checkout-session"
        
        # Données pour un abonnement enseignant
        payload = {
            'subscription_type': 'teacher'
        }
        
        # En-têtes pour simuler une requête AJAX
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Envoi d'une requête POST à {endpoint}")
        logger.info(f"Payload: {payload}")
        
        # Envoyer la requête
        response = requests.post(endpoint, data=payload, headers=headers)
        
        # Vérifier la réponse
        logger.info(f"Code de statut: {response.status_code}")
        logger.info(f"Réponse: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'checkout_url' in data:
                logger.info(f"[SUCCÈS] URL de paiement générée: {data['checkout_url']}")
                return True
            else:
                logger.error(f"[ÉCHEC] Réponse sans URL de paiement: {data}")
                return False
        else:
            logger.error(f"[ÉCHEC] Statut HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"[ERREUR] Exception lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== VÉRIFICATION DE LA CORRECTION DU PAIEMENT ENSEIGNANT ===")
    
    success = test_payment_route()
    
    if success:
        logger.info("[SUCCÈS] La route de paiement fonctionne correctement!")
        print("\n[SUCCÈS] La route de paiement fonctionne correctement!")
        sys.exit(0)
    else:
        logger.error("[ÉCHEC] La route de paiement ne fonctionne pas correctement.")
        print("\n[ÉCHEC] La route de paiement ne fonctionne pas correctement.")
        sys.exit(1)
