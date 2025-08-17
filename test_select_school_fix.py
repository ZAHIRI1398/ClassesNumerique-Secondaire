"""
Script de test pour la correction de la route /payment/select-school
Ce script permet de tester la solution en local avant déploiement
"""
import requests
import os
import sys
import json
import argparse
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"  # URL locale par défaut
LOGIN_URL = f"{BASE_URL}/login"
DIAGNOSE_URL = f"{BASE_URL}/diagnose/select-school-route"
FIX_URL = f"{BASE_URL}/fix-payment/select-school"
OUTPUT_DIR = "test_results"

# Couleurs pour la console
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Affiche un texte formaté comme en-tête"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}\n")

def print_success(text):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Affiche un message d'erreur"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text):
    """Affiche un avertissement"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text):
    """Affiche une information"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def login(session, email, password):
    """Connexion à l'application"""
    print_info(f"Tentative de connexion avec l'utilisateur {email}...")
    
    # Récupérer le token CSRF
    response = session.get(LOGIN_URL)
    if response.status_code != 200:
        print_error(f"Impossible d'accéder à la page de connexion: {response.status_code}")
        return False
    
    # Extraire le token CSRF (cette partie peut nécessiter des ajustements selon l'implémentation)
    # Cette méthode simple suppose que le token est dans un input avec name="csrf_token"
    import re
    csrf_token = None
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if match:
        csrf_token = match.group(1)
    
    if not csrf_token:
        print_warning("Impossible de trouver le token CSRF. Tentative de connexion sans token...")
    
    # Données de connexion
    login_data = {
        "email": email,
        "password": password
    }
    
    if csrf_token:
        login_data["csrf_token"] = csrf_token
    
    # Envoi de la requête de connexion
    response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    
    # Vérifier si la connexion a réussi (redirection vers la page d'accueil)
    if "Déconnexion" in response.text or "Dashboard" in response.text:
        print_success(f"Connexion réussie avec {email}")
        return True
    else:
        print_error(f"Échec de la connexion avec {email}")
        return False

def test_diagnose_route(session):
    """Teste la route de diagnostic"""
    print_info("Test de la route de diagnostic...")
    
    response = session.get(DIAGNOSE_URL)
    
    if response.status_code == 200:
        print_success(f"Accès réussi à la route de diagnostic: {response.status_code}")
        
        # Sauvegarder la réponse HTML
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(OUTPUT_DIR, f"diagnose_result_{timestamp}.html")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print_info(f"Résultat sauvegardé dans {filename}")
        
        # Analyse simple du contenu
        if "Écoles avec abonnement actif" in response.text:
            print_success("La page de diagnostic contient les informations sur les écoles")
        else:
            print_warning("La page de diagnostic ne semble pas contenir les informations sur les écoles")
        
        return True
    elif response.status_code == 403:
        print_error(f"Accès refusé à la route de diagnostic: {response.status_code}")
        print_warning("Vérifiez que l'utilisateur a le rôle 'admin'")
        return False
    else:
        print_error(f"Erreur lors de l'accès à la route de diagnostic: {response.status_code}")
        return False

def test_fix_route(session):
    """Teste la route corrigée"""
    print_info("Test de la route corrigée...")
    
    response = session.get(FIX_URL)
    
    if response.status_code == 200:
        print_success(f"Accès réussi à la route corrigée: {response.status_code}")
        
        # Sauvegarder la réponse HTML
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(OUTPUT_DIR, f"fix_result_{timestamp}.html")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print_info(f"Résultat sauvegardé dans {filename}")
        
        # Analyse simple du contenu
        if "École" in response.text and "choisir" in response.text.lower():
            print_success("La page corrigée semble afficher la liste des écoles")
        else:
            print_warning("La page corrigée ne semble pas afficher la liste des écoles")
        
        return True
    elif response.status_code == 302:
        print_warning(f"Redirection détectée: {response.status_code}")
        print_info("La route a probablement redirigé vers une autre page (comportement normal si aucune école n'est trouvée)")
        return True
    else:
        print_error(f"Erreur lors de l'accès à la route corrigée: {response.status_code}")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Test de la correction de la route select-school")
    parser.add_argument("--email", help="Email de l'administrateur", required=True)
    parser.add_argument("--password", help="Mot de passe de l'administrateur", required=True)
    parser.add_argument("--url", help=f"URL de base (par défaut: {BASE_URL})", default=BASE_URL)
    
    args = parser.parse_args()
    
    # Mise à jour de l'URL de base si spécifiée
    global BASE_URL, LOGIN_URL, DIAGNOSE_URL, FIX_URL
    if args.url != BASE_URL:
        BASE_URL = args.url
        LOGIN_URL = f"{BASE_URL}/login"
        DIAGNOSE_URL = f"{BASE_URL}/diagnose/select-school-route"
        FIX_URL = f"{BASE_URL}/fix-payment/select-school"
    
    print_header("Test de la correction de la route select-school")
    print_info(f"URL de base: {BASE_URL}")
    
    # Créer une session pour conserver les cookies
    session = requests.Session()
    
    # Étape 1: Connexion
    if not login(session, args.email, args.password):
        print_error("Impossible de continuer les tests sans être connecté")
        sys.exit(1)
    
    # Étape 2: Test de la route de diagnostic
    diagnose_success = test_diagnose_route(session)
    
    # Étape 3: Test de la route corrigée
    fix_success = test_fix_route(session)
    
    # Résumé
    print_header("Résumé des tests")
    if diagnose_success:
        print_success("Route de diagnostic: OK")
    else:
        print_error("Route de diagnostic: ÉCHEC")
    
    if fix_success:
        print_success("Route corrigée: OK")
    else:
        print_error("Route corrigée: ÉCHEC")
    
    if diagnose_success and fix_success:
        print_success("Tous les tests ont réussi!")
        print_info("La correction peut être déployée en production")
    else:
        print_error("Certains tests ont échoué")
        print_warning("Vérifiez les erreurs avant de déployer en production")

if __name__ == "__main__":
    main()
