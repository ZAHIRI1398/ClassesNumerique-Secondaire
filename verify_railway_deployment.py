"""
Script de vérification du déploiement sur Railway

Ce script permet de vérifier le statut du déploiement des corrections d'affichage d'images
sur Railway en effectuant des requêtes HTTP vers les routes de correction et en analysant
les réponses.

Utilisation:
    python verify_railway_deployment.py --url https://votre-app.railway.app

"""

import argparse
import requests
import sys
import re
import time
from colorama import init, Fore, Style
from bs4 import BeautifulSoup

# Initialiser colorama pour les couleurs dans la console
init()

def print_success(message):
    """Affiche un message de succès en vert"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Affiche un message d'erreur en rouge"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Affiche un message d'avertissement en jaune"""
    print(f"{Fore.YELLOW}! {message}{Style.RESET_ALL}")

def print_info(message):
    """Affiche un message d'information en bleu"""
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

def print_header(message):
    """Affiche un en-tête en gras"""
    print(f"\n{Style.BRIGHT}{message}{Style.RESET_ALL}")
    print("=" * len(message))

def check_route(session, base_url, route, expected_text=None, description=None):
    """
    Vérifie une route spécifique et analyse la réponse
    
    Args:
        session: Session requests
        base_url: URL de base de l'application
        route: Route à vérifier
        expected_text: Texte attendu dans la réponse
        description: Description de la vérification
        
    Returns:
        bool: True si la vérification est réussie, False sinon
    """
    url = f"{base_url}/{route}"
    print_info(f"Vérification de {url}...")
    
    try:
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            if expected_text and expected_text not in response.text:
                print_warning(f"La route {route} a répondu avec le code 200 mais le texte attendu '{expected_text}' n'a pas été trouvé.")
                return False
            
            # Analyse du contenu pour détecter des erreurs
            soup = BeautifulSoup(response.text, 'html.parser')
            error_texts = ["error", "exception", "traceback", "failed", "échec", "erreur"]
            
            # Vérifier si des messages d'erreur sont présents dans le texte
            for error_text in error_texts:
                if error_text in response.text.lower():
                    # Vérifier si c'est une vraie erreur ou juste une mention
                    if re.search(r'error.*occurred|exception.*raised|traceback|failed to|échec de|erreur.*survenue', 
                                response.text.lower(), re.IGNORECASE):
                        print_error(f"Message d'erreur détecté dans la réponse de {route}: '{error_text}'")
                        return False
            
            print_success(f"La route {route} a répondu avec succès" + (f" - {description}" if description else ""))
            return True
        else:
            print_error(f"La route {route} a répondu avec le code {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur lors de la vérification de {route}: {str(e)}")
        return False

def check_image_display(session, base_url, exercise_type, exercise_id=None):
    """
    Vérifie l'affichage des images pour un type d'exercice spécifique
    
    Args:
        session: Session requests
        base_url: URL de base de l'application
        exercise_type: Type d'exercice à vérifier
        exercise_id: ID de l'exercice à vérifier (optionnel)
        
    Returns:
        bool: True si la vérification est réussie, False sinon
    """
    # Si un ID d'exercice est fourni, vérifier cet exercice spécifique
    if exercise_id:
        url = f"{base_url}/exercise/{exercise_id}"
    else:
        # Sinon, essayer de trouver un exercice du type spécifié
        url = f"{base_url}/exercises?type={exercise_type}"
    
    print_info(f"Vérification de l'affichage des images pour le type '{exercise_type}'...")
    
    try:
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Vérifier si des images sont présentes
            images = soup.find_all('img')
            cloudinary_images = [img for img in images if 'cloudinary' in img.get('src', '')]
            
            if cloudinary_images:
                print_success(f"Images Cloudinary trouvées pour le type '{exercise_type}'")
                return True
            else:
                print_warning(f"Aucune image Cloudinary trouvée pour le type '{exercise_type}'")
                return False
        else:
            print_error(f"Erreur lors de l'accès à l'exercice de type '{exercise_type}': code {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur lors de la vérification des images pour le type '{exercise_type}': {str(e)}")
        return False

def check_cloudinary_config(session, base_url):
    """
    Vérifie la configuration Cloudinary
    
    Args:
        session: Session requests
        base_url: URL de base de l'application
        
    Returns:
        bool: True si la configuration est correcte, False sinon
    """
    url = f"{base_url}/debug-cloudinary"
    print_info(f"Vérification de la configuration Cloudinary...")
    
    try:
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            if "cloudinary_cloud_name" in response.text and "is_configured: True" in response.text:
                print_success("Configuration Cloudinary correcte")
                return True
            else:
                print_error("Configuration Cloudinary incorrecte ou incomplète")
                return False
        else:
            print_warning(f"Route de debug Cloudinary non disponible (code {response.status_code})")
            return None
    
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur lors de la vérification de la configuration Cloudinary: {str(e)}")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Vérification du déploiement sur Railway")
    parser.add_argument("--url", required=True, help="URL de base de l'application Railway (ex: https://votre-app.railway.app)")
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    
    # Créer une session pour conserver les cookies
    session = requests.Session()
    
    print_header("VÉRIFICATION DU DÉPLOIEMENT DES CORRECTIONS D'AFFICHAGE D'IMAGES")
    print_info(f"URL de base: {base_url}")
    print()
    
    # Étape 1: Vérifier que l'application est en ligne
    print_header("1. VÉRIFICATION DE L'APPLICATION")
    app_online = check_route(session, base_url, "", None, "L'application est en ligne")
    
    if not app_online:
        print_error("L'application n'est pas accessible. Vérifiez l'URL et le statut du déploiement.")
        sys.exit(1)
    
    # Étape 2: Vérifier les routes de correction
    print_header("2. VÉRIFICATION DES ROUTES DE CORRECTION")
    
    routes_to_check = [
        ("check-image-consistency", None, "Vérification de la cohérence des chemins d'images"),
        ("sync-image-paths", None, "Synchronisation des chemins d'images"),
        ("fix-template-paths", None, "Correction des templates"),
        ("create-simple-placeholders", None, "Création d'images placeholder")
    ]
    
    routes_success = all(check_route(session, base_url, route, expected, desc) for route, expected, desc in routes_to_check)
    
    # Étape 3: Vérifier la configuration Cloudinary
    print_header("3. VÉRIFICATION DE LA CONFIGURATION CLOUDINARY")
    cloudinary_config = check_cloudinary_config(session, base_url)
    
    # Étape 4: Vérifier l'affichage des images par type d'exercice
    print_header("4. VÉRIFICATION DE L'AFFICHAGE DES IMAGES PAR TYPE D'EXERCICE")
    
    exercise_types = [
        "qcm",
        "fill_in_blanks",
        "legend",
        "underline_words",
        "word_placement",
        "qcm_multichoix",
        "dictation",
        "word_search"
    ]
    
    # Attendre un peu pour que les modifications prennent effet
    print_info("Attente de 5 secondes pour que les modifications prennent effet...")
    time.sleep(5)
    
    image_display_success = all(check_image_display(session, base_url, exercise_type) for exercise_type in exercise_types)
    
    # Résumé final
    print_header("RÉSUMÉ DU DÉPLOIEMENT")
    
    if app_online and routes_success and (cloudinary_config is True or cloudinary_config is None) and image_display_success:
        print_success("DÉPLOIEMENT RÉUSSI! Toutes les vérifications ont passé avec succès.")
        print_info("Les corrections d'affichage d'images ont été correctement déployées et sont fonctionnelles.")
    else:
        print_warning("DÉPLOIEMENT PARTIELLEMENT RÉUSSI")
        print_info("Certaines vérifications ont échoué. Consultez les messages ci-dessus pour plus de détails.")
        
        if not routes_success:
            print_warning("- Les routes de correction n'ont pas toutes fonctionné correctement.")
        
        if cloudinary_config is False:
            print_warning("- La configuration Cloudinary semble incorrecte.")
        
        if not image_display_success:
            print_warning("- L'affichage des images n'est pas optimal pour tous les types d'exercices.")
    
    print("\nPour plus de détails, consultez le guide de vérification: GUIDE_VERIFICATION_DEPLOIEMENT_IMAGES.md")

if __name__ == "__main__":
    main()
