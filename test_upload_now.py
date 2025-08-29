import requests
import os
from PIL import Image

print("=== TEST UPLOAD AVEC DEBUG ===")

# Créer une image de test simple
test_img = Image.new('RGB', (100, 100), color='red')
test_path = "test_debug_upload.png"
test_img.save(test_path)

file_size = os.path.getsize(test_path)
print(f"Image de test créée: {test_path} ({file_size} octets)")

print("\n=== INSTRUCTIONS ===")
print("1. Allez sur: http://127.0.0.1:5000/exercise/4/edit")
print(f"2. Uploadez l'image: {test_path}")
print("3. Sauvegardez l'exercice")
print("4. Surveillez les logs Flask pour voir:")
print("   - DEBUG: Taille fichier initial: X octets")
print("   - DEBUG: Position fichier avant save: X")
print("   - DEBUG: Position fichier après save: X")
print("   - Fichier sauvegardé avec succès OU ERREUR")

print("\n=== APRÈS L'UPLOAD ===")
print("Exécutez: python check_latest_upload.py")
print("pour vérifier si le fichier a été sauvegardé correctement.")

print(f"\nImage de test prête: {test_path}")
print("Flask est maintenant configuré avec les logs de debug.")
