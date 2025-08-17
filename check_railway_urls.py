import requests
import sys
import time

def check_railway_url(url, max_attempts=2):
    """
    Vérifie si une URL Railway est accessible
    
    Args:
        url (str): L'URL à vérifier
        max_attempts (int): Nombre de tentatives
        
    Returns:
        tuple: (est_accessible, code_statut)
    """
    print(f"Vérification de l'URL: {url}")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=10)
            status_code = response.status_code
            
            if status_code == 200:
                print(f"[SUCCES] URL accessible (code {status_code})")
                return True, status_code
            else:
                print(f"[ECHEC] Code de réponse: {status_code}")
                return False, status_code
        
        except requests.RequestException as e:
            print(f"[ERREUR] {str(e)}")
            
        if attempt < max_attempts:
            print("Nouvelle tentative...")
            time.sleep(2)
    
    return False, None

def check_multiple_urls():
    """
    Vérifie plusieurs variantes d'URL possibles pour l'application Railway
    """
    # Liste des URL possibles pour l'application Railway
    urls = [
        "https://classesnumerique-secondaire-production.up.railway.app/",
        "https://classesnumerique-secondaire-production.up.railway.app",
        "https://classesnumerique-secondaire.up.railway.app/",
        "https://classesnumerique-secondaire.up.railway.app",
        "https://classesnumerique-secondaire-production.railway.app/",
        "https://classesnumerique-production.up.railway.app/",
        "https://classesnumerique.up.railway.app/"
    ]
    
    # Vérifier chaque URL
    results = []
    for url in urls:
        success, status_code = check_railway_url(url)
        results.append((url, success, status_code))
        print("-" * 50)
    
    # Afficher un résumé
    print("\nRÉSUMÉ DES RÉSULTATS:")
    print("=" * 70)
    for url, success, status_code in results:
        status = f"[OK] Code {status_code}" if success else f"[ECHEC] Code {status_code if status_code else 'N/A'}"
        print(f"{url:<60} {status}")
    
    # Vérifier si au moins une URL est accessible
    if any(success for _, success, _ in results):
        print("\n[SUCCES] Au moins une URL est accessible!")
        return True
    else:
        print("\n[ECHEC] Aucune URL n'est accessible. Le déploiement a peut-être échoué.")
        return False

if __name__ == "__main__":
    success = check_multiple_urls()
    sys.exit(0 if success else 1)
