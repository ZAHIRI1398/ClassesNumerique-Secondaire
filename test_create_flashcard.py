import requests
import json
from urllib.parse import urljoin
import os
import time

# Configuration
base_url = "http://127.0.0.1:5000"
login_url = urljoin(base_url, "/login")
create_exercise_url = urljoin(base_url, "/create_exercise_simple")
test_image_path = "static/uploads/test_flashcard_image.png"

# Informations de connexion (à adapter selon votre configuration)
login_data = {
    "email": "admin@classesnumeriques.com",
    "password": "AdminSecure2024!"
}

# Création d'une image de test si elle n'existe pas
def create_test_image():
    if not os.path.exists(test_image_path):
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Création d'une image simple
            img = Image.new('RGB', (300, 200), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((10, 10), "Image Test Flashcard", fill=(255, 255, 0))
            
            # Création du répertoire si nécessaire
            os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
            
            # Sauvegarde de l'image
            img.save(test_image_path)
            print(f"Image de test créée: {test_image_path}")
        except Exception as e:
            print(f"Erreur lors de la création de l'image de test: {str(e)}")
            # Créer un fichier texte à la place
            os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
            with open(test_image_path, 'w') as f:
                f.write("Test image content")
            print(f"Fichier texte de test créé à la place: {test_image_path}")

# Fonction principale
def test_create_flashcard():
    # Création de l'image de test
    create_test_image()
    
    # Création d'une session pour maintenir les cookies
    session = requests.Session()
    
    # Connexion à l'application
    print("Tentative de connexion...")
    try:
        response = session.post(login_url, data=login_data)
        if response.status_code == 200:
            print("Connexion réussie!")
        else:
            print(f"Échec de la connexion. Statut: {response.status_code}")
            print(f"Réponse: {response.text}")
            return
    except Exception as e:
        print(f"Erreur lors de la connexion: {str(e)}")
        return
    
    # Préparation des données pour la création d'un exercice flashcard
    print("\nPréparation des données pour la création d'un exercice flashcard...")
    
    # Données de l'exercice
    exercise_data = {
        "title": f"Test Flashcard Auto {int(time.time())}",
        "description": "Exercice de test créé automatiquement",
        "exercise_type": "flashcards",
        "subject": "Mathématiques",
        "card_question_0": "Question de test 1",
        "card_answer_0": "Réponse de test 1",
        "card_question_1": "Question de test 2",
        "card_answer_1": "Réponse de test 2",
    }
    
    # Fichiers à uploader
    files = {
        "card_image_0": ("test_image.png", open(test_image_path, "rb"), "image/png"),
        "card_image_1": ("test_image.png", open(test_image_path, "rb"), "image/png"),
    }
    
    # Envoi de la requête
    print("Envoi de la requête de création d'exercice...")
    try:
        response = session.post(create_exercise_url, data=exercise_data, files=files)
        if response.status_code == 200:
            print("Création de l'exercice réussie!")
            print(f"Réponse: {response.text[:200]}...")  # Affiche les 200 premiers caractères
        else:
            print(f"Échec de la création de l'exercice. Statut: {response.status_code}")
            print(f"Réponse: {response.text}")
    except Exception as e:
        print(f"Erreur lors de la création de l'exercice: {str(e)}")
    
    # Fermeture des fichiers
    for file in files.values():
        file[1].close()

if __name__ == "__main__":
    test_create_flashcard()
