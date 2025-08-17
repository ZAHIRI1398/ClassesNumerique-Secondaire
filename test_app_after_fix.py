import requests
import time
import sys

def test_app_after_fix():
    """
    Teste si l'application Flask fonctionne correctement après la correction de l'erreur OSError.
    """
    print("Test de l'application après correction de l'erreur OSError...")
    
    # URL de base de l'application
    base_url = "http://127.0.0.1:5000"
    
    # Attendre que l'application démarre complètement
    print("Attente du démarrage complet de l'application...")
    time.sleep(3)
    
    # Test 1: Vérifier que la page d'accueil est accessible
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("[OK] Page d'accueil accessible")
        else:
            print(f"[ERREUR] Page d'accueil inaccessible. Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception lors de l'accès à la page d'accueil: {str(e)}")
        return False
    
    # Test 2: Vérifier que l'exercice 2 est accessible
    try:
        response = requests.get(f"{base_url}/exercise/2")
        if response.status_code == 200:
            print("[OK] Exercice 2 accessible")
        else:
            print(f"[ERREUR] Exercice 2 inaccessible. Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] Exception lors de l'accès à l'exercice 2: {str(e)}")
        return False
    
    print("\n[SUCCÈS] L'application fonctionne correctement après la correction de l'erreur OSError.")
    return True

if __name__ == "__main__":
    success = test_app_after_fix()
    if not success:
        print("\n[ÉCHEC] L'application ne fonctionne pas correctement après la correction.")
        sys.exit(1)
    else:
        print("\nLa correction de l'erreur OSError a été validée avec succès!")
        sys.exit(0)
