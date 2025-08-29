#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour diagnostiquer les routes Flask en temps réel
"""

import requests
import sys
import json

def test_flask_routes():
    """Teste les routes Flask disponibles"""
    base_url = "http://127.0.0.1:5000"
    
    # Routes à tester
    routes_to_test = [
        "/",
        "/test_upload", 
        "/login",
        "/register",
        "/teacher/dashboard"
    ]
    
    print("=== DIAGNOSTIC DES ROUTES FLASK ===")
    print(f"URL de base: {base_url}")
    print()
    
    for route in routes_to_test:
        url = f"{base_url}{route}"
        try:
            response = requests.get(url, timeout=5)
            status = response.status_code
            
            if status == 200:
                print(f"✅ {route} -> {status} (OK)")
            elif status == 404:
                print(f"❌ {route} -> {status} (NOT FOUND)")
            elif status == 302:
                print(f"🔄 {route} -> {status} (REDIRECT)")
            elif status == 500:
                print(f"💥 {route} -> {status} (SERVER ERROR)")
            else:
                print(f"⚠️  {route} -> {status}")
                
        except requests.exceptions.ConnectionError:
            print(f"🔌 {route} -> CONNECTION REFUSED (Flask non démarré?)")
        except requests.exceptions.Timeout:
            print(f"⏱️  {route} -> TIMEOUT")
        except Exception as e:
            print(f"❓ {route} -> ERROR: {e}")
    
    print()
    
    # Test spécifique pour /test_upload
    print("=== TEST SPÉCIFIQUE /test_upload ===")
    try:
        response = requests.get(f"{base_url}/test_upload", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.status_code == 404:
            print("Contenu de la réponse 404:")
            print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
    except Exception as e:
        print(f"Erreur lors du test /test_upload: {e}")

if __name__ == "__main__":
    test_flask_routes()
