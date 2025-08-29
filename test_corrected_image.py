import requests
import time

# Attendre que Flask démarre puis tester l'image corrigée
base_url = "http://127.0.0.1:5000"
image_url = f"{base_url}/static/uploads/Capture d'écran 2025-08-12 174224_20250823_145200_M3pzNU.png"
exercise_url = f"{base_url}/exercise/4"

print("=== TEST DE L'IMAGE CORRIGÉE ===")

# Attendre que Flask soit prêt
for i in range(10):
    try:
        response = requests.get(base_url, timeout=2)
        print("Flask est démarré!")
        break
    except:
        print(f"Attente Flask... ({i+1}/10)")
        time.sleep(2)
else:
    print("Flask ne répond pas")
    exit(1)

# Test de l'image corrigée
try:
    img_response = requests.get(image_url)
    print(f"Image: {img_response.status_code} ({len(img_response.content)} octets)")
    
    if img_response.status_code == 200 and len(img_response.content) > 0:
        print("[OK] Image accessible et valide")
    else:
        print("[ERROR] Problème avec l'image")
        
except Exception as e:
    print(f"[ERROR] Erreur image: {e}")

# Test de l'exercice
try:
    ex_response = requests.get(exercise_url)
    print(f"Exercice: {ex_response.status_code}")
    
    if "145200_M3pzNU" in ex_response.text:
        print("[OK] Chemin d'image trouvé dans le HTML")
    else:
        print("[WARNING] Chemin d'image non trouvé dans le HTML")
        
except Exception as e:
    print(f"[ERROR] Erreur exercice: {e}")

print("\n=== INSTRUCTIONS ===")
print("1. Ouvrez l'exercice QCM dans votre navigateur")
print("2. Actualisez avec Ctrl+F5 pour forcer le rechargement")
print("3. L'image de l'appareil digestif devrait maintenant s'afficher")
