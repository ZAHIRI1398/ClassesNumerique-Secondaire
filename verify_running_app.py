#!/usr/bin/env python3
"""
Vérifier quelle version de l'application Flask est en cours d'exécution
"""

import requests
import time

def verify_running_app():
    """Vérifier l'application Flask en cours d'exécution"""
    
    print("=== VERIFICATION APPLICATION FLASK EN COURS ===\n")
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Vérifier que l'app répond
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✓ Application répond sur {base_url}")
        print(f"  Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Application ne répond pas: {e}")
        return
    
    # Test 2: Tester /test_upload directement
    try:
        response = requests.get(f"{base_url}/test_upload", timeout=5)
        print(f"\nTest /test_upload:")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✓ Route accessible")
            print(f"  Content-Length: {len(response.content)} bytes")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        elif response.status_code == 404:
            print(f"  ✗ Route retourne 404")
            print(f"  Réponse: {response.text[:200]}")
        else:
            print(f"  ? Status inattendu: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Erreur requête: {e}")
    
    # Test 3: Tester une route qui devrait exister
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        print(f"\nTest route /login (contrôle):")
        print(f"  Status: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print(f"  ✓ Route de contrôle fonctionne")
        else:
            print(f"  ? Status inattendu pour /login: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Erreur requête /login: {e}")
    
    # Test 4: Tester avec différents User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(f"{base_url}/test_upload", headers=headers, timeout=5)
        print(f"\nTest /test_upload avec User-Agent navigateur:")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✓ Fonctionne avec User-Agent navigateur")
        else:
            print(f"  ✗ Même problème avec User-Agent navigateur")
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Erreur avec User-Agent: {e}")

if __name__ == "__main__":
    verify_running_app()
