import requests
import json
import sys
from flask import Flask, session
import os

# Configuration
BASE_URL = "http://127.0.0.1:5000"
EXERCISE_ID = 2  # ID de l'exercice 2 (Texte à trous - Les verbes)

def test_scoring():
    """Teste le scoring de l'exercice 2 avec différentes réponses."""
    print("=== Test de scoring pour l'exercice 2 (Texte à trous - Les verbes) ===")
    
    # Test 1: Réponses correctes
    test_answers_correct = ["suis", "es"]
    print(f"\nTest 1: Réponses correctes {test_answers_correct}")
    score = simulate_submission(test_answers_correct)
    print(f"Score obtenu: {score}%")
    
    # Test 2: Réponses dans l'ordre inverse
    test_answers_reversed = ["es", "suis"]
    print(f"\nTest 2: Réponses dans l'ordre inverse {test_answers_reversed}")
    score = simulate_submission(test_answers_reversed)
    print(f"Score obtenu: {score}%")
    
    # Test 3: Une réponse correcte, une incorrecte
    test_answers_partial = ["suis", "incorrect"]
    print(f"\nTest 3: Une réponse correcte, une incorrecte {test_answers_partial}")
    score = simulate_submission(test_answers_partial)
    print(f"Score obtenu: {score}%")
    
    # Test 4: Réponses incorrectes
    test_answers_wrong = ["incorrect1", "incorrect2"]
    print(f"\nTest 4: Réponses incorrectes {test_answers_wrong}")
    score = simulate_submission(test_answers_wrong)
    print(f"Score obtenu: {score}%")

def simulate_submission(answers):
    """Simule une soumission d'exercice avec les réponses données."""
    try:
        # Créer une application Flask pour simuler une session
        app = Flask(__name__)
        app.secret_key = 'test_key'
        
        with app.test_request_context():
            # Simuler une session avec un utilisateur connecté
            session['user_id'] = 1
            session['user_type'] = 'student'
            
            # Préparer les données pour la soumission
            data = {
                'exercise_id': EXERCISE_ID,
                'answers[]': answers
            }
            
            # Effectuer la requête POST pour soumettre l'exercice
            response = requests.post(
                f"{BASE_URL}/submit_exercise",
                data=data,
                cookies={'session': 'dummy_session'}
            )
            
            # Analyser la réponse
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result.get('score', 0)
                except json.JSONDecodeError:
                    print("Erreur: Réponse non-JSON reçue")
                    print(f"Contenu de la réponse: {response.text[:200]}...")
                    return None
            else:
                print(f"Erreur: Code de statut {response.status_code}")
                print(f"Contenu de la réponse: {response.text[:200]}...")
                return None
    except Exception as e:
        print(f"Erreur lors de la simulation: {e}")
        return None

def check_exercise_structure():
    """Vérifie la structure de l'exercice 2 dans l'application."""
    try:
        # Récupérer les détails de l'exercice
        response = requests.get(f"{BASE_URL}/exercise/{EXERCISE_ID}")
        
        if response.status_code == 200:
            print("\n=== Structure de l'exercice 2 ===")
            # Analyser le HTML pour extraire les informations pertinentes
            html = response.text
            
            # Vérifier le type d'exercice
            if "Texte à trous" in html:
                print("Type d'exercice: Texte à trous ✓")
            
            # Vérifier la présence de champs de saisie
            input_count = html.count('<input type="text"')
            print(f"Nombre de champs de saisie: {input_count}")
            
            # Vérifier si le formulaire de soumission est présent
            if 'action="/submit_exercise"' in html:
                print("Formulaire de soumission présent ✓")
            
            return True
        else:
            print(f"Erreur lors de la récupération de l'exercice: {response.status_code}")
            return False
    except Exception as e:
        print(f"Erreur lors de la vérification de la structure: {e}")
        return False

if __name__ == "__main__":
    print("Démarrage des tests de scoring pour l'exercice 2...")
    
    # Vérifier que l'application est en cours d'exécution
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"Erreur: L'application n'est pas accessible. Code: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Erreur: Impossible de se connecter à l'application. Assurez-vous qu'elle est en cours d'exécution.")
        sys.exit(1)
    
    # Vérifier la structure de l'exercice
    if check_exercise_structure():
        # Exécuter les tests de scoring
        test_scoring()
    else:
        print("Impossible de continuer les tests en raison d'erreurs dans la structure de l'exercice.")
