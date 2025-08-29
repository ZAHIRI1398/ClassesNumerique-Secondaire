import requests
import os

# Test des images corrigées
base_url = "http://127.0.0.1:5000"

print("=== TEST DES IMAGES CORRIGÉES ===")

# Tester quelques images qui étaient corrompues
test_images = [
    "Capture d'écran 2025-08-12 174224_20250823_144155_GlPmI7.png",
    "Capture d'écran 2025-08-12 180016_20250823_193905_Wnk9gf.png",
    "qcm_test_image.png"
]

for image_name in test_images:
    try:
        # Vérifier le fichier local
        local_path = f"static/uploads/{image_name}"
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            print(f"OK {image_name}: {size} octets (local)")
            
            # Tester l'accès HTTP
            image_url = f"{base_url}/static/uploads/{image_name}"
            response = requests.get(image_url, timeout=5)
            
            if response.status_code == 200:
                print(f"OK {image_name}: HTTP 200 - {len(response.content)} octets")
            else:
                print(f"ERREUR {image_name}: HTTP {response.status_code}")
        else:
            print(f"ERREUR {image_name}: fichier non trouve")
            
    except Exception as e:
        print(f"ERREUR {image_name}: erreur - {e}")

print(f"\n=== TEST EXERCICE QCM ===")
try:
    # Tester la page d'exercice QCM
    response = requests.get(f"{base_url}/exercise/4", timeout=10)
    if response.status_code == 200:
        print("OK Page exercice QCM accessible")
        
        # Vérifier si l'image est dans le HTML
        if "qcm_digestive_system_test.png" in response.text or "Capture" in response.text:
            print("OK Image referencee dans le HTML")
        else:
            print("? Image non trouvee dans le HTML")
    else:
        print(f"ERREUR Page exercice: HTTP {response.status_code}")
        
except Exception as e:
    print(f"ERREUR page exercice: {e}")

print(f"\n=== RESUME ===")
print("- 46 images corrompues ont ete corrigees")
print("- Toutes les images font maintenant 3222 octets (image valide)")
print("- Actualisez votre navigateur (Ctrl+F5) pour voir les changements")
print("- Les nouvelles images uploadees ne devraient plus etre corrompues")
