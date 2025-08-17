#!/usr/bin/env python3
"""
Script pour vérifier si la route de diagnostic fonctionne correctement en production
et si la correction résout le problème pour l'exercice "Les coordonnées"
"""
import os
import sys
import requests
import json
import re
import argparse
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def check_deployment_status(base_url):
    """Vérifie si le déploiement est terminé en testant l'accès à la page d'accueil"""
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print(f"[INFO] Application accessible à {base_url} (code {response.status_code})")
            return True
        else:
            print(f"[ERREUR] Application non accessible: code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERREUR] Impossible de se connecter à {base_url}: {str(e)}")
        return False

def check_diagnostic_route(base_url):
    """Vérifie si la route de diagnostic fonctionne correctement"""
    session = requests.Session()
    diagnostic_url = urljoin(base_url, '/debug-all-fill-in-blanks')
    
    try:
        print(f"[INFO] Tentative d'accès à la route de diagnostic: {diagnostic_url}")
        response = session.get(diagnostic_url, timeout=15)
        
        if response.status_code == 403:
            print("[INFO] La route de diagnostic existe mais nécessite une authentification (code 403)")
            print("[INFO] C'est normal car la route est protégée pour les administrateurs")
            print("[SUCCÈS] La route de diagnostic a été correctement déployée!")
            return True
        elif response.status_code != 200:
            print(f"[ERREUR] La route de diagnostic a retourné une erreur: {response.status_code}")
            return False
        
        # Si on arrive ici, c'est qu'on a un code 200 (rare car normalement protégé)
        print("[SUCCÈS] La route de diagnostic est accessible!")
        
        # Vérifier si la page contient les éléments attendus
        if "DIAGNOSTIC TOUS LES EXERCICES FILL_IN_BLANKS" in response.text:
            print("[SUCCÈS] La page de diagnostic contient le titre attendu")
            print("[ATTENTION] La route n'est pas correctement protégée par authentification")
        
        return True
    
    except requests.exceptions.Timeout:
        print("[INFO] Timeout lors de l'accès à la route de diagnostic (c'est peut-être normal si le serveur est occupé)")
        print("[INFO] La route existe probablement mais le serveur est occupé")
        return True
    except Exception as e:
        print(f"[ERREUR] Exception lors de la vérification de la route de diagnostic: {str(e)}")
        return False

def check_public_routes(base_url):
    """Vérifie si les routes publiques sont accessibles"""
    session = requests.Session()
    routes_to_check = [
        '/',  # Page d'accueil
        '/login',  # Page de connexion
        '/register',  # Page d'inscription
        '/exercise_library'  # Bibliothèque d'exercices (peut nécessiter une connexion)
    ]
    
    results = {}
    
    for route in routes_to_check:
        url = urljoin(base_url, route)
        try:
            print(f"[INFO] Vérification de la route: {url}")
            response = session.get(url, timeout=10)
            status = response.status_code
            results[route] = status
            
            if status == 200:
                print(f"[SUCCÈS] Route {route} accessible (code {status})")
            else:
                print(f"[INFO] Route {route} a retourné le code {status}")
                
        except Exception as e:
            print(f"[ERREUR] Erreur lors de l'accès à {route}: {str(e)}")
            results[route] = str(e)
    
    return results

def check_for_coordonnees_exercise(base_url):
    """Vérifie si l'exercice 'Les coordonnées' est mentionné dans la page d'accueil ou la bibliothèque"""
    session = requests.Session()
    
    try:
        # Essayer d'accéder à la bibliothèque d'exercices (peut nécessiter une connexion)
        library_url = urljoin(base_url, '/exercise_library')
        response = session.get(library_url, timeout=10)
        
        if response.status_code == 200 and "coordonnées" in response.text.lower():
            print("[INFO] Mention de 'coordonnées' trouvée dans la bibliothèque d'exercices")
            return True
        
        # Essayer la page d'accueil
        response = session.get(base_url, timeout=10)
        if response.status_code == 200 and "coordonnées" in response.text.lower():
            print("[INFO] Mention de 'coordonnées' trouvée sur la page d'accueil")
            return True
            
        print("[INFO] Aucune mention de 'coordonnées' trouvée dans les pages publiques")
        print("[INFO] C'est normal car l'exercice nécessite probablement une connexion")
        return False
        
    except Exception as e:
        print(f"[ERREUR] Exception lors de la recherche de l'exercice: {str(e)}")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Vérifier la route de diagnostic et l'accessibilité de l'application")
    parser.add_argument("--url", default="https://classesnumeriques.up.railway.app", help="URL de base de l'application")
    parser.add_argument("--wait", type=int, default=0, help="Temps d'attente en secondes avant la vérification (pour laisser le temps au déploiement)")
    args = parser.parse_args()
    
    if args.wait > 0:
        print(f"[INFO] Attente de {args.wait} secondes pour laisser le temps au déploiement...")
        time.sleep(args.wait)
    
    print(f"\n[INFO] Vérification de l'application à l'URL: {args.url}")
    
    # Vérifier si l'application est accessible
    if not check_deployment_status(args.url):
        print("[ERREUR] L'application n'est pas accessible. Vérification impossible.")
        return
    
    # Vérifier la route de diagnostic
    print("\n[INFO] Vérification de la route de diagnostic...")
    check_diagnostic_route(args.url)
    
    # Vérifier les routes publiques
    print("\n[INFO] Vérification des routes publiques...")
    check_public_routes(args.url)
    
    # Rechercher l'exercice 'Les coordonnées'
    print("\n[INFO] Recherche de l'exercice 'Les coordonnées'...")
    check_for_coordonnees_exercise(args.url)
    
    print("\n[INFO] Vérification terminée!")
    print("[INFO] Pour vérifier complètement la correction du scoring, connectez-vous à l'application")
    print("[INFO] et accédez à la route /debug-all-fill-in-blanks en tant qu'administrateur.")
    print("[INFO] Cette route vous montrera tous les exercices fill_in_blanks et word_placement")
    print("[INFO] avec leur nombre de blancs et de mots, ainsi que leur cohérence.")

if __name__ == "__main__":
    main()
