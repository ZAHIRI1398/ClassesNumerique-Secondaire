import requests
import json

# Test de la route /get_cloudinary_url
base_url = "http://127.0.0.1:5000"

# Liste des chemins d'images à tester
image_paths = [
    "uploads/1756247392_3opwru.png",
    "uploads/1756247392_o1p7u4.png",
    "uploads/1756247392_sfnq84.png",
    "uploads/1756307741_mox2ot.png",
    "uploads/1756307741_fpxlrz.png",
    "uploads/1756307741_gl8wuh.png"
]

print("Test de la route /get_cloudinary_url :")
print("-" * 50)

for image_path in image_paths:
    try:
        # Appel à la route /get_cloudinary_url
        response = requests.get(f"{base_url}/get_cloudinary_url", params={"image_path": image_path})
        
        # Vérification du statut de la réponse
        if response.status_code == 200:
            data = response.json()
            print(f"Image: {image_path}")
            print(f"Statut: Succès (200)")
            print(f"URL: {data.get('url', 'Non disponible')}")
        else:
            print(f"Image: {image_path}")
            print(f"Statut: Échec ({response.status_code})")
            print(f"Réponse: {response.text}")
        
        print("-" * 50)
    except Exception as e:
        print(f"Image: {image_path}")
        print(f"Erreur: {str(e)}")
        print("-" * 50)
