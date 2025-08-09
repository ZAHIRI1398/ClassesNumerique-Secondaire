#!/usr/bin/env python3
"""
Test script pour diagnostiquer l'erreur sur l'exercice 7 "Souligner les mots"
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000"
EXERCISE_ID = 7

def test_exercise_view():
    """Test d'affichage de l'exercice"""
    print("=== TEST 1: Affichage de l'exercice ===")
    try:
        url = f"{BASE_URL}/exercise/{EXERCISE_ID}/0"
        response = requests.get(url)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("OK L'exercice s'affiche correctement")
            # Vérifier si le formulaire contient la bonne action
            if 'handle_exercise_answer' in response.text:
                print("OK Le formulaire utilise la route handle_exercise_answer")
            else:
                print("ERREUR Le formulaire n'utilise pas la route handle_exercise_answer")
        else:
            print(f"ERREUR Erreur d'affichage: {response.status_code}")
            print(response.text[:500])
    except Exception as e:
        print(f"ERREUR Erreur lors du test d'affichage: {e}")

def test_exercise_submission():
    """Test de soumission de l'exercice"""
    print("\n=== TEST 2: Soumission de l'exercice ===")
    try:
        url = f"{BASE_URL}/exercise/{EXERCISE_ID}/answer"
        
        # Données de test basées sur l'exercice 7
        data = {
            'selected_words_0': 'dort',  # Phrase 1: "le chat noir dort sur le canapé"
            'selected_words_1': 'suis',  # Phrase 2: "je suis un bon élève"
            'selected_words_2': 'suis,travailler',  # Phrase 3: "je suis ravis de travailler avec vous"
            'course_id': '0'
        }
        
        print(f"URL: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("OK La soumission fonctionne")
            # Vérifier si c'est une redirection ou du JSON
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    result = response.json()
                    print(f"Réponse JSON: {json.dumps(result, indent=2)}")
                except:
                    print("Réponse non-JSON reçue")
            else:
                print("Réponse HTML reçue (probablement une redirection)")
        elif response.status_code == 302:
            print("OK Redirection reçue (comportement normal)")
            print(f"Location: {response.headers.get('Location', 'Non spécifiée')}")
        elif response.status_code == 404:
            print("ERREUR Route non trouvée (404)")
        elif response.status_code == 500:
            print("ERREUR Erreur serveur (500)")
            print("Première partie de la réponse:")
            print(response.text[:1000])
        else:
            print(f"ERREUR Erreur inattendue: {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"ERREUR Erreur lors du test de soumission: {e}")

def test_exercise_data():
    """Test des données de l'exercice en base"""
    print("\n=== TEST 3: Données de l'exercice en base ===")
    try:
        # Import des modèles Flask
        import sys
        sys.path.append('.')
        from app import app
        from models import Exercise
        
        with app.app_context():
            exercise = Exercise.query.get(EXERCISE_ID)
            if exercise:
                print(f"OK Exercice trouvé: {exercise.title}")
                print(f"Type: {exercise.exercise_type}")
                
                content = exercise.get_content()
                print(f"Structure du contenu:")
                print(f"- Clés disponibles: {list(content.keys()) if isinstance(content, dict) else 'Non-dict'}")
                
                if 'words' in content:
                    print(f"- Nombre de phrases (words): {len(content['words'])}")
                    for i, sentence in enumerate(content['words']):
                        print(f"  Phrase {i}: {sentence.get('text', 'TEXTE MANQUANT')}")
                        print(f"  Mots à souligner: {sentence.get('words_to_underline', 'MANQUANT')}")
                
                if 'sentences' in content:
                    print(f"- Nombre de phrases (sentences): {len(content['sentences'])}")
                    
            else:
                print(f"ERREUR Exercice {EXERCISE_ID} non trouvé en base")
                
    except Exception as e:
        print(f"ERREUR Erreur lors du test des données: {e}")

if __name__ == "__main__":
    print("DIAGNOSTIC EXERCICE 7 - SOULIGNER LES MOTS")
    print("=" * 50)
    
    test_exercise_view()
    test_exercise_submission()
    test_exercise_data()
    
    print("\n" + "=" * 50)
    print("FIN DU DIAGNOSTIC")
