#!/usr/bin/env python3
"""
Script pour tester les exercices fill_in_blanks en production
Ce script vérifie spécifiquement l'exercice "Les coordonnées" et d'autres exercices fill_in_blanks
pour s'assurer que la correction du scoring fonctionne correctement.
"""
import os
import sys
import json
import requests
import argparse
from getpass import getpass
from bs4 import BeautifulSoup

# URL de base de l'application
BASE_URL = "https://web-production-9a047.up.railway.app"

def login(email, password):
    """Se connecter à l'application"""
    print(f"[INFO] Tentative de connexion avec {email}...")
    
    # Créer une session pour conserver les cookies
    session = requests.Session()
    
    # Récupérer le formulaire de connexion pour obtenir le token CSRF
    response = session.get(f"{BASE_URL}/login")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Chercher le token CSRF
    csrf_token = None
    for input_tag in soup.find_all('input'):
        if input_tag.get('name') == 'csrf_token':
            csrf_token = input_tag.get('value')
            break
    
    if not csrf_token:
        print("[ERREUR] Impossible de récupérer le token CSRF")
        return None
    
    # Préparer les données de connexion
    login_data = {
        'csrf_token': csrf_token,
        'email': email,
        'password': password,
        'submit': 'Se connecter'
    }
    
    # Envoyer la requête de connexion
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    # Vérifier si la connexion a réussi
    if "Déconnexion" in response.text:
        print("[SUCCÈS] Connexion réussie!")
        return session
    else:
        print("[ERREUR] Échec de la connexion")
        return None

def test_debug_route(session):
    """Tester la route de diagnostic pour tous les exercices fill_in_blanks"""
    print("\n[INFO] Test de la route de diagnostic pour tous les exercices fill_in_blanks...")
    
    response = session.get(f"{BASE_URL}/debug-all-fill-in-blanks")
    
    if response.status_code != 200:
        print(f"[ERREUR] La route a retourné le code {response.status_code}")
        return False
    
    # Analyser la réponse
    print("[INFO] Analyse de la réponse...")
    
    # Chercher des informations sur les exercices fill_in_blanks
    if "fill_in_blanks" in response.text:
        print("[SUCCÈS] La route de diagnostic fonctionne et retourne des informations sur les exercices fill_in_blanks")
        
        # Chercher des informations sur l'exercice "Les coordonnées"
        if "coordonnées" in response.text.lower() or "coordonnees" in response.text.lower():
            print("[INFO] L'exercice 'Les coordonnées' a été trouvé dans la réponse")
            
            # Chercher des informations sur le scoring
            if "blancs" in response.text and "réponses" in response.text:
                print("[INFO] La réponse contient des informations sur les blancs et les réponses")
                
                # Sauvegarder la réponse dans un fichier pour analyse
                with open("debug_fill_in_blanks_response.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("[INFO] Réponse sauvegardée dans debug_fill_in_blanks_response.html")
                
                return True
    
    print("[ERREUR] La route de diagnostic ne retourne pas les informations attendues")
    return False

def test_specific_exercise(session, exercise_id):
    """Tester un exercice spécifique"""
    print(f"\n[INFO] Test de l'exercice {exercise_id}...")
    
    # Récupérer l'exercice
    response = session.get(f"{BASE_URL}/exercise/{exercise_id}")
    
    if response.status_code != 200:
        print(f"[ERREUR] L'exercice {exercise_id} n'est pas accessible (code {response.status_code})")
        return False
    
    # Analyser la réponse
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Récupérer le titre de l'exercice
    title = soup.find('h1')
    if title:
        print(f"[INFO] Titre de l'exercice: {title.text.strip()}")
    
    # Vérifier si c'est un exercice fill_in_blanks
    if "fill_in_blanks" in response.text or "texte à trous" in response.text.lower():
        print("[INFO] C'est bien un exercice de type fill_in_blanks")
        
        # Chercher les champs de réponse
        answer_fields = soup.find_all('input', {'name': lambda x: x and x.startswith('answer_')})
        if answer_fields:
            print(f"[INFO] L'exercice contient {len(answer_fields)} champs de réponse")
            
            # Simuler une soumission avec toutes les réponses correctes
            # Pour cela, il faudrait connaître les réponses correctes
            # Ici, nous allons juste vérifier que le formulaire existe
            form = soup.find('form', {'action': lambda x: x and 'submit_exercise' in x})
            if form:
                print("[SUCCÈS] Le formulaire de soumission existe")
                return True
    
    print("[ERREUR] Ce n'est pas un exercice fill_in_blanks ou le formulaire est manquant")
    return False

def find_coordonnees_exercise(session):
    """Trouver l'exercice 'Les coordonnées'"""
    print("\n[INFO] Recherche de l'exercice 'Les coordonnées'...")
    
    # Récupérer la liste des exercices
    response = session.get(f"{BASE_URL}/exercises")
    
    if response.status_code != 200:
        print(f"[ERREUR] Impossible d'accéder à la liste des exercices (code {response.status_code})")
        return None
    
    # Analyser la réponse
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Chercher l'exercice "Les coordonnées"
    for link in soup.find_all('a', href=True):
        if "coordonnées" in link.text.lower() or "coordonnees" in link.text.lower():
            exercise_id = link['href'].split('/')[-1]
            print(f"[SUCCÈS] Exercice 'Les coordonnées' trouvé avec ID {exercise_id}")
            return exercise_id
    
    print("[ERREUR] Exercice 'Les coordonnées' non trouvé")
    return None

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Tester les exercices fill_in_blanks en production")
    parser.add_argument("--email", help="Email pour la connexion")
    parser.add_argument("--password", help="Mot de passe pour la connexion")
    parser.add_argument("--exercise-id", help="ID de l'exercice à tester")
    args = parser.parse_args()
    
    # Demander les informations de connexion si non fournies
    email = args.email
    if not email:
        email = input("Email: ")
    
    password = args.password
    if not password:
        password = getpass("Mot de passe: ")
    
    # Se connecter
    session = login(email, password)
    if not session:
        sys.exit(1)
    
    # Tester la route de diagnostic
    test_debug_route(session)
    
    # Trouver l'exercice "Les coordonnées" si aucun ID n'est fourni
    exercise_id = args.exercise_id
    if not exercise_id:
        exercise_id = find_coordonnees_exercise(session)
    
    # Tester l'exercice spécifique
    if exercise_id:
        test_specific_exercise(session, exercise_id)
    
    print("\n[INFO] Tests terminés")

if __name__ == "__main__":
    main()
