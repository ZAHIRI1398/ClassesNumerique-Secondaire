#!/usr/bin/env python3
"""
Test direct de la route test_upload
"""

import os
import sys

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_route_direct():
    """Tester la route test_upload directement"""
    
    print("=== TEST DIRECT ROUTE /test_upload ===\n")
    
    with app.test_client() as client:
        # Test GET
        print("Test GET /test_upload:")
        response = client.get('/test_upload')
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        
        if response.status_code == 200:
            print("SUCCESS: Route accessible")
            print(f"Response length: {len(response.data)} bytes")
        elif response.status_code == 404:
            print("ERROR: Route retourne 404")
        else:
            print(f"ERROR: Status code inattendu: {response.status_code}")
        
        # Afficher les headers de réponse
        print("\nHeaders de réponse:")
        for header, value in response.headers:
            print(f"  {header}: {value}")
        
        # Si erreur, afficher le contenu
        if response.status_code != 200:
            print(f"\nContenu de la réponse:")
            print(response.data.decode('utf-8')[:500])

if __name__ == "__main__":
    test_route_direct()
