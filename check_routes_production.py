#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour vérifier les routes en production après déploiement
Ce script teste les redirections du flux d'abonnement
"""

import os
import sys
import logging
import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"check_routes_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("check_routes_production")

def check_route(base_url, route, expected_status=None, expected_redirect=None, follow_redirects=False):
    """
    Vérifie une route spécifique et ses redirections
    
    Args:
        base_url (str): URL de base de l'application
        route (str): Route à vérifier (sans le base_url)
        expected_status (int, optional): Code de statut HTTP attendu
        expected_redirect (str, optional): URL de redirection attendue
        follow_redirects (bool, optional): Si True, suit les redirections
        
    Returns:
        dict: Résultat de la vérification
    """
    url = urljoin(base_url, route)
    logger.info(f"Vérification de la route: {url}")
    
    try:
        response = requests.get(url, allow_redirects=follow_redirects)
        status_code = response.status_code
        
        result = {
            "url": url,
            "status_code": status_code,
            "success": True
        }
        
        # Vérifier le code de statut
        if expected_status and status_code != expected_status:
            logger.warning(f"Code de statut inattendu: {status_code} (attendu: {expected_status})")
            result["success"] = False
        else:
            logger.info(f"Code de statut: {status_code}")
        
        # Vérifier la redirection
        if 300 <= status_code < 400:
            redirect_url = response.headers.get('Location')
            result["redirect_url"] = redirect_url
            
            if expected_redirect:
                expected_full_url = urljoin(base_url, expected_redirect)
                if redirect_url != expected_full_url:
                    logger.warning(f"Redirection inattendue: {redirect_url} (attendu: {expected_full_url})")
                    result["success"] = False
                else:
                    logger.info(f"Redirection correcte vers: {redirect_url}")
            else:
                logger.info(f"Redirection vers: {redirect_url}")
        
        # Vérifier le contenu si on suit les redirections
        if follow_redirects:
            result["final_url"] = response.url
            logger.info(f"URL finale après redirections: {response.url}")
            
            # Vérifier si la page contient certains éléments
            if "select_school" in route:
                if "Aucune école avec un abonnement actif" in response.text:
                    logger.warning("Message 'Aucune école avec un abonnement actif' détecté")
                    result["no_schools_message"] = True
                else:
                    logger.info("Pas de message d'erreur concernant les écoles")
                    result["no_schools_message"] = False
        
        return result
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de {url}: {str(e)}")
        return {
            "url": url,
            "success": False,
            "error": str(e)
        }

def check_subscription_flow(base_url):
    """
    Vérifie le flux complet d'abonnement
    
    Args:
        base_url (str): URL de base de l'application
        
    Returns:
        bool: True si le flux est correct, False sinon
    """
    logger.info("=" * 80)
    logger.info("VÉRIFICATION DU FLUX D'ABONNEMENT")
    logger.info("=" * 80)
    
    # Étape 1: Accès à la page de choix d'abonnement
    subscription_choice = check_route(
        base_url, 
        "/subscription-choice", 
        expected_status=200,
        follow_redirects=True
    )
    
    # Étape 2: Redirection vers la route subscribe/school
    subscribe_school = check_route(
        base_url, 
        "/payment/subscribe/school", 
        expected_status=302,
        expected_redirect="/payment/select_school"
    )
    
    # Étape 3: Accès à la page de sélection d'école
    select_school = check_route(
        base_url, 
        "/payment/select_school", 
        expected_status=200,
        follow_redirects=True
    )
    
    # Vérifier si le flux est correct
    flow_success = all([
        subscription_choice.get("success", False),
        subscribe_school.get("success", False),
        select_school.get("success", False)
    ])
    
    if flow_success:
        logger.info("✅ Le flux d'abonnement semble fonctionner correctement")
    else:
        logger.error("❌ Le flux d'abonnement présente des problèmes")
    
    return flow_success

def check_all_routes(base_url):
    """
    Vérifie toutes les routes importantes de l'application
    
    Args:
        base_url (str): URL de base de l'application
        
    Returns:
        dict: Résultats des vérifications
    """
    results = {}
    
    # Routes principales
    routes = [
        "/",
        "/login",
        "/register",
        "/subscription-choice",
        "/payment/subscribe/school",
        "/payment/subscribe/teacher",
        "/payment/select_school"
    ]
    
    for route in routes:
        results[route] = check_route(base_url, route, follow_redirects=True)
    
    return results

def main():
    """Fonction principale"""
    # URL de base de l'application en production
    base_url = os.environ.get('PRODUCTION_APP_URL')
    if not base_url:
        logger.error("❌ La variable d'environnement PRODUCTION_APP_URL n'est pas définie")
        logger.info("Pour exécuter ce script, définissez la variable d'environnement avec l'URL de l'application en production")
        logger.info("Exemple: set PRODUCTION_APP_URL=https://votre-application.up.railway.app")
        sys.exit(1)
    
    logger.info(f"Vérification des routes pour: {base_url}")
    
    # Vérifier le flux d'abonnement
    subscription_flow_success = check_subscription_flow(base_url)
    
    # Vérifier toutes les routes importantes
    logger.info("\n" + "=" * 80)
    logger.info("VÉRIFICATION DE TOUTES LES ROUTES")
    logger.info("=" * 80)
    all_routes_results = check_all_routes(base_url)
    
    # Résumé
    logger.info("\n" + "=" * 80)
    logger.info("RÉSUMÉ DES VÉRIFICATIONS")
    logger.info("=" * 80)
    
    success_count = sum(1 for result in all_routes_results.values() if result.get("success", False))
    total_count = len(all_routes_results)
    
    logger.info(f"Routes vérifiées: {total_count}")
    logger.info(f"Routes fonctionnelles: {success_count}")
    logger.info(f"Routes avec problèmes: {total_count - success_count}")
    
    if subscription_flow_success:
        logger.info("✅ Le flux d'abonnement fonctionne correctement")
    else:
        logger.error("❌ Le flux d'abonnement présente des problèmes")
    
    # Liste des routes avec problèmes
    problem_routes = [route for route, result in all_routes_results.items() if not result.get("success", False)]
    if problem_routes:
        logger.warning("Routes avec problèmes:")
        for route in problem_routes:
            logger.warning(f"  - {route}")
    
    logger.info("=" * 80)
    logger.info("FIN DE LA VÉRIFICATION")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
