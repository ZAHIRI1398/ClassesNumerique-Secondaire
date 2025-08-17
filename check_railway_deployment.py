import requests
import sys
import time

def check_railway_deployment(url, max_attempts=5, delay=5):
    """
    Vérifie si le déploiement Railway est fonctionnel en testant l'URL spécifiée.
    
    Args:
        url (str): L'URL de l'application déployée sur Railway
        max_attempts (int): Nombre maximum de tentatives
        delay (int): Délai entre les tentatives en secondes
        
    Returns:
        bool: True si le déploiement est fonctionnel, False sinon
    """
    print(f"Vérification du déploiement Railway à l'URL: {url}")
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Tentative {attempt}/{max_attempts}...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"[SUCCES] L'application est en ligne (code {response.status_code})")
                return True
            else:
                print(f"[ECHEC] L'application a répondu avec le code {response.status_code}")
        
        except requests.RequestException as e:
            print(f"[ERREUR] Erreur lors de la connexion: {str(e)}")
        
        if attempt < max_attempts:
            print(f"Attente de {delay} secondes avant la prochaine tentative...")
            time.sleep(delay)
    
    print("[ECHEC] Le déploiement n'a pas pu être vérifié après plusieurs tentatives.")
    return False

if __name__ == "__main__":
    # URL par défaut ou URL fournie en argument
    url = sys.argv[1] if len(sys.argv) > 1 else "https://classesnumerique-secondaire-production.up.railway.app/"
    
    success = check_railway_deployment(url)
    
    # Code de sortie pour indiquer le succès ou l'échec
    sys.exit(0 if success else 1)
