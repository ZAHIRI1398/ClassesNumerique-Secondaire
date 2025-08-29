import requests
import json
from bs4 import BeautifulSoup

# Configuration
base_url = "http://127.0.0.1:5000"
exercise_id = 70  # ID d'un exercice flashcard existant

# Test de l'affichage des images dans l'interface d'édition
def test_edit_flashcard_images():
    # URL de la page d'édition
    edit_url = f"{base_url}/edit_exercise/{exercise_id}"
    
    print(f"Test de l'édition de l'exercice flashcard (ID: {exercise_id}):")
    print("-" * 50)
    
    try:
        # Récupération de la page d'édition
        response = requests.get(edit_url)
        
        if response.status_code == 200:
            print(f"Accès à la page d'édition: Succès (200)")
            
            # Analyse du HTML avec BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Recherche des éléments d'image dans la page
            image_previews = soup.select('.card-image-preview')
            image_inputs = soup.select('input[type="file"][name^="card_image_"]')
            
            print(f"Nombre d'aperçus d'images trouvés: {len(image_previews)}")
            print(f"Nombre de champs d'upload d'images trouvés: {len(image_inputs)}")
            
            # Vérification des appels JavaScript à la fonction loadImagePreview
            scripts = soup.find_all('script')
            js_image_calls = []
            
            for script in scripts:
                if script.string and 'loadImagePreview' in script.string:
                    js_image_calls.append(script.string)
            
            print(f"Nombre d'appels JavaScript à loadImagePreview: {len(js_image_calls)}")
            
            # Vérification des appels à /get_cloudinary_url
            cloudinary_calls = []
            for script in scripts:
                if script.string and '/get_cloudinary_url' in script.string:
                    cloudinary_calls.append(script.string)
            
            print(f"Nombre d'appels à /get_cloudinary_url: {len(cloudinary_calls)}")
            
            # Conclusion
            if len(image_previews) > 0 and len(image_inputs) > 0 and len(js_image_calls) > 0:
                print("\nRésultat: La page d'édition contient tous les éléments nécessaires pour l'affichage des images.")
                print("Les images devraient s'afficher correctement dans l'interface d'édition.")
            else:
                print("\nRésultat: Certains éléments nécessaires pour l'affichage des images sont manquants.")
                print("Les images pourraient ne pas s'afficher correctement dans l'interface d'édition.")
        else:
            print(f"Accès à la page d'édition: Échec ({response.status_code})")
            print(f"Réponse: {response.text[:200]}...")  # Affiche les 200 premiers caractères
    
    except Exception as e:
        print(f"Erreur lors du test: {str(e)}")

if __name__ == "__main__":
    test_edit_flashcard_images()
