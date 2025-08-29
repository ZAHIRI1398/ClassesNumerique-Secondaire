import requests
import os
from pathlib import Path

# Test d'upload d'une nouvelle image pour vérifier la correction
base_url = "http://127.0.0.1:5000"

print("=== TEST NOUVEAU UPLOAD ===")

# Chercher des images dans le bureau
bureau_path = Path.home() / "Desktop" / "Images"
if not bureau_path.exists():
    bureau_path = Path.home() / "Desktop"

print(f"Recherche d'images dans: {bureau_path}")

# Trouver une image de test
test_image = None
for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif']:
    images = list(bureau_path.glob(ext))
    if images:
        test_image = images[0]
        break

if test_image and test_image.exists():
    print(f"Image trouvée: {test_image.name} ({test_image.stat().st_size} octets)")
    
    print("\n=== INSTRUCTIONS POUR TESTER ===")
    print("1. Allez sur http://127.0.0.1:5000/exercise/4/edit")
    print("2. Cliquez sur 'Choisir un fichier' pour l'image")
    print(f"3. Sélectionnez l'image: {test_image}")
    print("4. Cliquez sur 'Sauvegarder les modifications'")
    print("5. Vérifiez les logs Flask pour voir:")
    print("   - 'Fichier sauvegardé avec succès: ... (X octets)'")
    print("   - PAS de 'ERREUR: Fichier sauvegardé avec 0 octets'")
    
    print("\n=== VÉRIFICATION APRÈS UPLOAD ===")
    print("Après avoir uploadé, exécutez ce script pour vérifier:")
    
else:
    print("Aucune image trouvée dans le bureau.")
    print("Créons une image de test...")
    
    # Créer une image de test simple
    from PIL import Image, ImageDraw
    
    test_img = Image.new('RGB', (300, 200), color='lightgreen')
    draw = ImageDraw.Draw(test_img)
    draw.text((50, 80), "Image de test", fill='black')
    
    test_path = "test_upload_image.png"
    test_img.save(test_path)
    
    print(f"Image de test créée: {test_path}")
    print("Utilisez cette image pour tester l'upload.")

print("\n=== SURVEILLANCE DES LOGS ===")
print("Surveillez la console Flask pour ces messages:")
print("OK 'CORRECTION: Remettre le pointeur du fichier au debut'")
print("OK 'Fichier sauvegarde avec succes: ... (X octets)'")
print("ERREUR 'ERREUR: Fichier sauvegarde avec 0 octets' (ne devrait plus apparaitre)")

# Vérifier les derniers fichiers uploadés
uploads_dir = "static/uploads"
if os.path.exists(uploads_dir):
    files = [(f, os.path.getmtime(os.path.join(uploads_dir, f))) 
             for f in os.listdir(uploads_dir) 
             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    # Trier par date de modification (plus récent en premier)
    files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n=== DERNIERS FICHIERS UPLOADÉS ===")
    for filename, mtime in files[:5]:
        filepath = os.path.join(uploads_dir, filename)
        size = os.path.getsize(filepath)
        status = "OK" if size > 0 else "CORROMPU"
        print(f"{status}: {filename} ({size} octets)")
