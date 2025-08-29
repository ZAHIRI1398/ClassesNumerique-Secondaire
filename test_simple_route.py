#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple pour vérifier les routes Flask
"""

import requests
import time

def test_routes():
    """Test simple des routes"""
    base_url = "http://127.0.0.1:5000"
    
    # Attendre que Flask soit prêt
    print("Attente du démarrage de Flask...")
    time.sleep(2)
    
    routes = ["/", "/test_upload"]
    
    for route in routes:
        try:
            url = f"{base_url}{route}"
            response = requests.get(url, timeout=10)
            print(f"{route}: {response.status_code}")
            
            if route == "/test_upload":
                if response.status_code == 200:
                    print("✅ Route /test_upload accessible!")
                else:
                    print(f"❌ Route /test_upload retourne {response.status_code}")
                    print("Contenu:", response.text[:200])
                    
        except requests.exceptions.ConnectionError:
            print(f"{route}: CONNECTION REFUSED")
        except Exception as e:
            print(f"{route}: ERROR - {e}")

if __name__ == "__main__":
    test_routes()
