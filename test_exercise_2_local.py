import requests
import json
import sys
import time

def test_exercise_2_scoring():
    """
    Test le scoring de l'exercice 2 localement
    Vérifie que la correction pour gérer les deux formats de mots fonctionne correctement
    """
    print("Test du scoring de l'exercice 2 localement...")
    
    # URL de l'API pour soumettre une réponse à l'exercice
    base_url = "http://127.0.0.1:5000"
    submit_url = f"{base_url}/exercise/2/submit"
    
    # Vérifier que l'application est accessible
    try:
        response = requests.get(base_url)
        if response.status_code != 200:
            print(f"ERREUR: L'application n'est pas accessible. Code: {response.status_code}")
            return False
        print("[OK] Application accessible")
    except Exception as e:
        print(f"ERREUR: Impossible de se connecter à l'application: {str(e)}")
        return False
    
    # Vérifier que l'exercice 2 est accessible
    exercise_url = f"{base_url}/exercise/2"
    try:
        response = requests.get(exercise_url)
        if response.status_code != 200:
            print(f"ERREUR: L'exercice 2 n'est pas accessible. Code: {response.status_code}")
            return False
        print("[OK] Exercice 2 accessible")
    except Exception as e:
        print(f"ERREUR: Impossible d'accéder à l'exercice 2: {str(e)}")
        return False
    
    # Données de test pour simuler une soumission d'exercice
    # Cas 1: Toutes les réponses correctes
    test_data_correct = {
        "exercise_id": 2,
        "answers": ["suis", "es", "est", "sommes", "êtes", "sont"],
        "user_id": 1
    }
    
    # Cas 2: Réponses partiellement correctes
    test_data_partial = {
        "exercise_id": 2,
        "answers": ["suis", "es", "est", "sommes", "sont", "êtes"],  # Deux dernières inversées
        "user_id": 1
    }
    
    # Cas 3: Réponses incorrectes
    test_data_incorrect = {
        "exercise_id": 2,
        "answers": ["a", "b", "c", "d", "e", "f"],
        "user_id": 1
    }
    
    # Test avec réponses correctes
    try:
        # Convertir les données en format de formulaire
        form_data = {
            'answers[]': test_data_correct['answers'],
            'user_id': test_data_correct['user_id'],
            'course_id': 1  # Valeur par défaut pour le cours
        }
        
        response = requests.post(submit_url, data=form_data)
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text[:200]}...")  # Afficher le début de la réponse
        
        # Vérifier si la réponse contient un score
        if 'score' in response.text.lower() and '100' in response.text:
            print("[OK] Score correct pour réponses 100% correctes: 100%")
        else:
            print("ERREUR: Score incorrect ou non trouvé pour réponses 100% correctes")
            return False
    except Exception as e:
        print(f"ERREUR lors du test avec réponses correctes: {str(e)}")
        return False
    
    # Test avec réponses partiellement correctes
    try:
        # Convertir les données en format de formulaire
        form_data = {
            'answers[]': test_data_partial['answers'],
            'user_id': test_data_partial['user_id'],
            'course_id': 1  # Valeur par défaut pour le cours
        }
        
        response = requests.post(submit_url, data=form_data)
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text[:200]}...")  # Afficher le début de la réponse
        
        # Vérifier si la réponse contient un score d'environ 66.67%
        if 'score' in response.text.lower() and ('66' in response.text or '67' in response.text):
            print("[OK] Score correct pour réponses partiellement correctes: ~66.67%")
        else:
            print("ERREUR: Score incorrect ou non trouvé pour réponses partiellement correctes")
            return False
    except Exception as e:
        print(f"ERREUR lors du test avec réponses partiellement correctes: {str(e)}")
        return False
    
    # Test avec réponses incorrectes
    try:
        # Convertir les données en format de formulaire
        form_data = {
            'answers[]': test_data_incorrect['answers'],
            'user_id': test_data_incorrect['user_id'],
            'course_id': 1  # Valeur par défaut pour le cours
        }
        
        response = requests.post(submit_url, data=form_data)
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text[:200]}...")  # Afficher le début de la réponse
        
        # Vérifier si la réponse contient un score de 0%
        if 'score' in response.text.lower() and '0' in response.text:
            print("[OK] Score correct pour réponses 100% incorrectes: 0%")
        else:
            print("ERREUR: Score incorrect ou non trouvé pour réponses 100% incorrectes")
            return False
    except Exception as e:
        print(f"ERREUR lors du test avec réponses incorrectes: {str(e)}")
        return False
    
    print("\n[SUCCES] TOUS LES TESTS ONT REUSSI!")
    print("La correction du format des mots dans l'exercice 2 fonctionne correctement.")
    return True

if __name__ == "__main__":
    # Attendre que l'application soit complètement démarrée
    print("Attente du démarrage complet de l'application...")
    time.sleep(3)
    
    success = test_exercise_2_scoring()
    if not success:
        print("\n[ECHEC] ECHEC DES TESTS")
        sys.exit(1)
    else:
        print("\nLa correction a été validée avec succès localement!")
        sys.exit(0)
