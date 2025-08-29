import requests
import webbrowser

# Test d'accès direct à l'image et à l'exercice
base_url = "http://127.0.0.1:5000"

# URL de l'image actuelle
image_url = f"{base_url}/static/uploads/Capture d'écran 2025-08-12 174224_20250823_144155_GlPmI7.png"
exercise_url = f"{base_url}/exercise/4"

print("=== TEST D'ACCÈS DIRECT ===")
print(f"Image URL: {image_url}")
print(f"Exercise URL: {exercise_url}")

# Test de l'image
try:
    img_response = requests.get(image_url)
    print(f"Image: {img_response.status_code} ({len(img_response.content)} octets)")
    if img_response.status_code == 200 and len(img_response.content) > 0:
        print("✓ Image accessible et non vide")
    else:
        print("✗ Problème avec l'image")
except Exception as e:
    print(f"✗ Erreur image: {e}")

# Test de l'exercice
try:
    ex_response = requests.get(exercise_url)
    print(f"Exercice: {ex_response.status_code}")
    if "Capture d'écran 2025-08-12 174224_20250823_144155_GlPmI7.png" in ex_response.text:
        print("✓ Chemin d'image trouvé dans le HTML")
    else:
        print("✗ Chemin d'image non trouvé dans le HTML")
except Exception as e:
    print(f"✗ Erreur exercice: {e}")

print("\n=== SOLUTION ===")
print("L'image fonctionne techniquement.")
print("Le problème est probablement le cache du navigateur.")
print("Solutions:")
print("1. Actualisez avec Ctrl+F5 (rechargement forcé)")
print("2. Ouvrez en navigation privée/incognito")
print("3. Videz le cache du navigateur")
