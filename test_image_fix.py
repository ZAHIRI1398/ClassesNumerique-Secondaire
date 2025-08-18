"""
Script de test des routes de diagnostic et correction d'images
"""

import os
import sys
import requests
import webbrowser
from urllib.parse import urljoin

def test_image_fix_routes(base_url="http://localhost:5000"):
    """
    Teste les routes de diagnostic et correction d'images
    
    Args:
        base_url: URL de base de l'application (par défaut: http://localhost:5000)
    """
    print("=== Test des routes de diagnostic et correction d'images ===")
    
    # Liste des routes à tester
    routes = [
        "/fix-uploads-directory",
        "/check-image-paths",
        "/create-placeholder-images"
    ]
    
    # Tester chaque route
    for route in routes:
        full_url = urljoin(base_url, route)
        print(f"\nTest de {full_url}...")
        
        try:
            # Envoyer une requête GET à la route
            response = requests.get(full_url, timeout=10)
            
            # Vérifier le code de statut
            if response.status_code == 200:
                print(f"✅ Succès (code {response.status_code})")
                
                # Pour les routes JSON, afficher le résultat
                if route != "/check-image-paths":
                    try:
                        data = response.json()
                        print(f"Réponse: {data}")
                    except:
                        print("Réponse non-JSON reçue")
                else:
                    print("Page HTML de diagnostic reçue")
                    
                # Ouvrir la route dans le navigateur
                print(f"Ouverture de {full_url} dans le navigateur...")
                webbrowser.open(full_url)
            else:
                print(f"❌ Échec (code {response.status_code})")
                print(f"Réponse: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
    
    print("\n=== Test terminé ===")
    print("Vérifiez les onglets ouverts dans votre navigateur pour voir les résultats complets.")

if __name__ == "__main__":
    # Utiliser l'URL fournie en argument ou l'URL par défaut
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    test_image_fix_routes(base_url)
