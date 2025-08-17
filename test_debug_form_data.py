#!/usr/bin/env python3
"""
Script pour tester la route de diagnostic /debug-form-data
"""

import requests
import json
import argparse
from bs4 import BeautifulSoup

def test_debug_form_data(url, email, password):
    """
    Teste la route de diagnostic /debug-form-data
    """
    session = requests.Session()
    
    # 1. Se connecter
    print(f"[INFO] Connexion à {url}/login")
    login_page = session.get(f"{url}/login")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value')
    
    login_data = {
        'email': email,
        'password': password,
        'csrf_token': csrf_token
    }
    
    login_response = session.post(f"{url}/login", data=login_data)
    if "Se déconnecter" not in login_response.text and "Logout" not in login_response.text:
        print("[ERREUR] Échec de la connexion")
        return
    
    print("[OK] Connexion réussie")
    
    # 2. Accéder à la route de diagnostic
    print(f"[INFO] Accès à la route de diagnostic /debug-form-data")
    debug_page = session.get(f"{url}/debug-form-data")
    
    if debug_page.status_code != 200:
        print(f"[ERREUR] Impossible d'accéder à la route de diagnostic: {debug_page.status_code}")
        return
    
    print("[OK] Accès à la route de diagnostic réussi")
    
    # 3. Analyser le formulaire de test
    soup = BeautifulSoup(debug_page.text, 'html.parser')
    form = soup.find('form', {'action': '/debug-form-data'})
    
    if not form:
        print("[ERREUR] Formulaire de test non trouvé")
        return
    
    # 4. Préparer les données du formulaire
    form_data = {
        'csrf_token': form.find('input', {'name': 'csrf_token'}).get('value'),
        'answer_0': 'test_mot_1',
        'answer_1': 'test_mot_2',
        'answer_2': 'test_mot_3',
        'answer_3': 'test_mot_4',
        'answer_4': 'test_mot_5'
    }
    
    print(f"[INFO] Données du formulaire préparées: {json.dumps(form_data, indent=2)}")
    
    # 5. Soumettre le formulaire
    print(f"[INFO] Soumission du formulaire de test")
    response = session.post(f"{url}/debug-form-data", data=form_data)
    
    if response.status_code != 200:
        print(f"[ERREUR] Échec de la soumission: {response.status_code}")
        return
    
    # 6. Analyser la réponse JSON
    try:
        result = response.json()
        print("\n[RÉSULTAT] Réponse du serveur:")
        print(json.dumps(result, indent=2))
        
        # Vérifier si tous les champs ont été reçus
        if 'form_data' in result:
            answer_fields = [key for key in result['form_data'].keys() if key.startswith('answer_')]
            print(f"\n[INFO] Champs 'answer_X' reçus: {len(answer_fields)}")
            for field in answer_fields:
                print(f"  - {field}: {result['form_data'][field]}")
            
            if len(answer_fields) == 5:
                print("\n[SUCCÈS] Tous les champs de formulaire ont été correctement reçus!")
            else:
                print(f"\n[ATTENTION] Certains champs manquent. Attendu: 5, Reçu: {len(answer_fields)}")
    except json.JSONDecodeError:
        print("[ERREUR] La réponse n'est pas au format JSON")
        print(response.text[:500])  # Afficher les 500 premiers caractères de la réponse

def main():
    parser = argparse.ArgumentParser(description="Test de la route de diagnostic /debug-form-data")
    parser.add_argument("--url", default="https://web-production-9a047.up.railway.app", help="URL de base")
    parser.add_argument("--email", required=True, help="Email de connexion (doit être admin)")
    parser.add_argument("--password", required=True, help="Mot de passe")
    
    args = parser.parse_args()
    
    test_debug_form_data(args.url, args.email, args.password)

if __name__ == "__main__":
    main()
