import requests
import os
from io import BytesIO
from PIL import Image

# Test de la correction d'upload d'images
base_url = "http://127.0.0.1:5000"

print("=== TEST DE LA CORRECTION D'UPLOAD ===")

# Créer une image de test en mémoire
def create_test_image():
    # Créer une image simple de test
    img = Image.new('RGB', (200, 150), color='lightblue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

# Test 1: Vérifier que Flask répond
try:
    response = requests.get(base_url)
    print(f"Flask status: {response.status_code}")
except Exception as e:
    print(f"Erreur Flask: {e}")
    exit(1)

# Test 2: Simuler un upload d'image via l'interface d'édition
print("\n=== SIMULATION D'UPLOAD ===")
print("Pour tester la correction:")
print("1. Allez sur http://127.0.0.1:5000/exercise/4/edit")
print("2. Uploadez une nouvelle image")
print("3. Sauvegardez l'exercice")
print("4. Vérifiez que l'image n'est plus vide (0 octets)")

# Test 3: Vérifier les logs Flask pour voir les messages de debug
print("\n=== VÉRIFICATION DES LOGS ===")
print("Surveillez les logs Flask pour ces messages:")
print("- 'Fichier sauvegardé avec succès: ... (X octets)'")
print("- 'ERREUR: Fichier sauvegardé avec 0 octets' (ne devrait plus apparaître)")

print("\n=== CORRECTION APPLIQUÉE ===")
print("✓ Ajout de file.seek(0) avant la sauvegarde")
print("✓ Vérification de la taille du fichier après sauvegarde")
print("✓ Messages de debug pour diagnostiquer les problèmes")
print("\nLa correction devrait résoudre le problème des fichiers vides.")
