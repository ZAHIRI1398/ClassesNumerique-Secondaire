#!/usr/bin/env python3
"""
Script pour s'authentifier et accéder à la route de diagnostic protégée
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

def login_to_app(base_url, email, password):
    """Se connecte à l'application et retourne la session"""
    session = requests.Session()
    
    # Récupérer le token CSRF
    login_url = urljoin(base_url, '/login')
    print(f"[INFO] Accès à la page de connexion: {login_url}")
    
    try:
        response = session.get(login_url, timeout=15)
        
        if response.status_code != 200:
            print(f"[ERREUR] Impossible d'accéder à la page de connexion: {response.status_code}")
            return None
        
        # Extraire le token CSRF
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token_input = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_token_input:
            print("[ERREUR] Impossible de trouver le champ csrf_token dans la page de connexion")
            return None
            
        csrf_token = csrf_token_input.get('value')
        
        if not csrf_token:
            print("[ERREUR] Impossible de récupérer le token CSRF")
            return None
        
        # Se connecter
        login_data = {
            'email': email,
            'password': password,
            'csrf_token': csrf_token
        }
        
        print(f"[INFO] Tentative de connexion avec l'email: {email}")
        response = session.post(login_url, data=login_data)
        
        if response.status_code != 200:
            print(f"[ERREUR] Échec de la connexion: {response.status_code}")
            return None
        
        # Vérifier si la connexion a réussi
        if "Se déconnecter" in response.text or "Logout" in response.text:
            print("[SUCCÈS] Connexion réussie!")
            return session
        else:
            print("[ERREUR] Échec de la connexion: identifiants incorrects")
            return None
        
    except Exception as e:
        print(f"[ERREUR] Exception lors de la connexion: {str(e)}")
        return None

def access_diagnostic_route(session, base_url):
    """Accède à la route de diagnostic et affiche les résultats"""
    if not session:
        print("[ERREUR] Session non valide, impossible d'accéder à la route de diagnostic")
        return False
    
    diagnostic_url = urljoin(base_url, '/debug-all-fill-in-blanks')
    print(f"[INFO] Accès à la route de diagnostic: {diagnostic_url}")
    
    try:
        response = session.get(diagnostic_url, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERREUR] Impossible d'accéder à la route de diagnostic: {response.status_code}")
            return False
        
        # Vérifier si la page contient les éléments attendus
        if "DIAGNOSTIC TOUS LES EXERCICES FILL_IN_BLANKS" not in response.text:
            print("[ERREUR] La page de diagnostic ne contient pas le titre attendu")
            return False
        
        print("[SUCCÈS] Accès à la route de diagnostic réussi!")
        
        # Analyser le contenu de la page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraire les informations d'environnement
        env_section = soup.find('h2', text=re.compile("Variables d'environnement"))
        if env_section:
            env_info = env_section.find_next('pre')
            if env_info:
                print("\n[INFO] Variables d'environnement:")
                print(env_info.text.strip())
        
        # Vérifier les tests de scoring
        test_sentences = soup.find(text=re.compile("Score avec sentences:"))
        test_text = soup.find(text=re.compile("Score avec text:"))
        
        if test_sentences and "100%" in test_sentences:
            print("\n[SUCCÈS] Test de scoring avec sentences réussi (100%)")
        else:
            print("\n[ERREUR] Test de scoring avec sentences échoué")
        
        if test_text and "100%" in test_text:
            print("[SUCCÈS] Test de scoring avec text réussi (100%)")
        else:
            print("[ERREUR] Test de scoring avec text échoué")
        
        # Rechercher l'exercice "Les coordonnées"
        print("\n[INFO] Recherche de l'exercice 'Les coordonnées'...")
        coordonnees_found = False
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2 and "coordonnées" in cells[1].text.lower():
                    coordonnees_found = True
                    print(f"[INFO] Exercice 'Les coordonnées' trouvé!")
                    
                    # Extraire toutes les informations de la ligne
                    exercise_info = {}
                    headers = table.find('tr').find_all('th')
                    header_texts = [h.text.strip() for h in headers]
                    
                    for i, cell in enumerate(cells):
                        if i < len(header_texts):
                            exercise_info[header_texts[i]] = cell.text.strip()
                    
                    # Afficher les informations
                    for key, value in exercise_info.items():
                        print(f"[INFO] {key}: {value}")
                    
                    # Vérifier la cohérence
                    if len(cells) >= 6:
                        coherence = cells[5].text.strip()
                        coherence_color = cells[5].get('style', '')
                        
                        if "✓" in coherence:
                            print("[SUCCÈS] L'exercice 'Les coordonnées' a une cohérence correcte entre blancs et mots!")
                        else:
                            print("[ERREUR] L'exercice 'Les coordonnées' a une incohérence entre blancs et mots")
                    break
            
            if coordonnees_found:
                break
        
        if not coordonnees_found:
            print("[ERREUR] Exercice 'Les coordonnées' non trouvé dans la liste")
        
        # Sauvegarder la page HTML pour analyse ultérieure
        with open("diagnostic_result.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("\n[INFO] Page de diagnostic sauvegardée dans 'diagnostic_result.html'")
        
        return True
    
    except Exception as e:
        print(f"[ERREUR] Exception lors de l'accès à la route de diagnostic: {str(e)}")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="S'authentifier et accéder à la route de diagnostic protégée")
    parser.add_argument("--url", default="https://web-production-9a047.up.railway.app", help="URL de base de l'application")
    parser.add_argument("--email", help="Email de l'administrateur")
    parser.add_argument("--password", help="Mot de passe de l'administrateur")
    args = parser.parse_args()
    
    # Vérifier les identifiants
    email = args.email or os.environ.get('ADMIN_EMAIL')
    password = args.password or os.environ.get('ADMIN_PASSWORD')
    
    if not email or not password:
        print("[ERREUR] Email et mot de passe requis. Utilisez --email et --password ou définissez ADMIN_EMAIL et ADMIN_PASSWORD")
        return
    
    print(f"[INFO] Connexion à l'application à l'URL: {args.url}")
    
    # Se connecter à l'application
    session = login_to_app(args.url, email, password)
    
    if not session:
        print("[ERREUR] Impossible de se connecter à l'application")
        return
    
    # Accéder à la route de diagnostic
    print("\n[INFO] Accès à la route de diagnostic...")
    access_diagnostic_route(session, args.url)
    
    print("\n[INFO] Vérification terminée!")

if __name__ == "__main__":
    main()
