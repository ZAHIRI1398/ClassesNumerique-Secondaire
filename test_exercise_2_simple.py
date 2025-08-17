import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:5000"
EXERCISE_ID = 2  # ID de l'exercice 2 (Texte à trous - Les verbes)

def test_scoring():
    """Teste le scoring de l'exercice 2 avec différentes réponses."""
    print("=== Test de scoring pour l'exercice 2 (Texte a trous - Les verbes) ===")
    
    # Test 1: Réponses correctes
    test_answers_correct = ["suis", "es"]
    print(f"\nTest 1: Reponses correctes {test_answers_correct}")
    score = simulate_submission(test_answers_correct)
    print(f"Score obtenu: {score}%")
    
    # Test 2: Réponses dans l'ordre inverse
    test_answers_reversed = ["es", "suis"]
    print(f"\nTest 2: Reponses dans l'ordre inverse {test_answers_reversed}")
    score = simulate_submission(test_answers_reversed)
    print(f"Score obtenu: {score}%")
    
    # Test 3: Une réponse correcte, une incorrecte
    test_answers_partial = ["suis", "incorrect"]
    print(f"\nTest 3: Une reponse correcte, une incorrecte {test_answers_partial}")
    score = simulate_submission(test_answers_partial)
    print(f"Score obtenu: {score}%")
    
    # Test 4: Réponses incorrectes
    test_answers_wrong = ["incorrect1", "incorrect2"]
    print(f"\nTest 4: Reponses incorrectes {test_answers_wrong}")
    score = simulate_submission(test_answers_wrong)
    print(f"Score obtenu: {score}%")

def simulate_submission(answers):
    """Simule une soumission d'exercice avec les réponses données."""
    try:
        # Préparer les données pour la soumission
        data = {
            'exercise_id': EXERCISE_ID,
            'answers[]': answers
        }
        
        # Effectuer la requête POST pour soumettre l'exercice
        response = requests.post(
            f"{BASE_URL}/submit_exercise",
            data=data
        )
        
        # Analyser la réponse
        if response.status_code == 200:
            try:
                result = response.json()
                return result.get('score', 0)
            except json.JSONDecodeError:
                print("Erreur: Reponse non-JSON recue")
                print(f"Contenu de la reponse: {response.text[:200]}...")
                return None
        else:
            print(f"Erreur: Code de statut {response.status_code}")
            print(f"Contenu de la reponse: {response.text[:200]}...")
            return None
    except Exception as e:
        print(f"Erreur lors de la simulation: {e}")
        return None

if __name__ == "__main__":
    print("Demarrage des tests de scoring pour l'exercice 2...")
    
    # Vérifier que l'application est en cours d'exécution
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"Erreur: L'application n'est pas accessible. Code: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Erreur: Impossible de se connecter a l'application. Assurez-vous qu'elle est en cours d'execution.")
        sys.exit(1)
    
    # Exécuter les tests de scoring
    test_scoring()
