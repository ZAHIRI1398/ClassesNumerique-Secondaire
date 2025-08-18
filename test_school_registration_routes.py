import requests
import sys
import os

def test_routes():
    """
    Test les routes d'inscription d'école pour vérifier qu'elles sont accessibles.
    """
    base_url = "http://127.0.0.1:5000"
    routes = [
        "/register-school-simplified",
        "/register-school-connected"
    ]
    
    results = {}
    
    print("Vérification des routes d'inscription d'école...")
    for route in routes:
        url = base_url + route
        try:
            response = requests.get(url)
            status_code = response.status_code
            if status_code == 200:
                results[route] = f"[OK] Accessible (code {status_code})"
            elif status_code == 302:
                results[route] = f"[ATTENTION] Redirection (code {status_code}) - Nécessite probablement une authentification"
            else:
                results[route] = f"[ERREUR] Erreur (code {status_code})"
        except Exception as e:
            results[route] = f"[ERREUR] Erreur: {str(e)}"
    
    print("\nRésultats des tests:")
    print("-" * 50)
    for route, result in results.items():
        print(f"{route}: {result}")
    print("-" * 50)
    
    # Vérifier si l'application est en cours d'exécution
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("[OK] L'application Flask est en cours d'exécution.")
        else:
            print(f"[ATTENTION] L'application Flask répond avec le code {response.status_code}.")
    except Exception as e:
        print(f"[ERREUR] L'application Flask n'est pas accessible: {str(e)}")
        print("Assurez-vous que l'application est en cours d'exécution avec 'python app.py'")

if __name__ == "__main__":
    test_routes()
