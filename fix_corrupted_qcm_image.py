import sqlite3
import json
import shutil
import os

# Corriger l'image QCM corrompue
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Récupérer l'exercice QCM
cursor.execute('SELECT id, title, content, image_path FROM exercise WHERE id = 4')
result = cursor.fetchone()

if result:
    exercise_id, title, content_json, image_path = result
    print(f"Exercice: {title}")
    
    # Parser le contenu
    content = json.loads(content_json)
    current_image = content.get('image')
    print(f"Image corrompue: {current_image}")
    
    # Chemin du fichier corrompu
    if current_image and current_image.startswith('/static/'):
        corrupted_file = current_image[1:]  # Enlever le / initial
        print(f"Fichier corrompu: {corrupted_file}")
        
        # Utiliser l'image de test fonctionnelle
        source_image = "static/uploads/qcm_digestive_system_test.png"
        if os.path.exists(source_image):
            print(f"Image source: {source_image}")
            
            # Vérifier que l'image source est valide
            source_size = os.path.getsize(source_image)
            print(f"Taille image source: {source_size} octets")
            
            if source_size > 0:
                # Copier l'image valide vers le fichier corrompu
                shutil.copy2(source_image, corrupted_file)
                new_size = os.path.getsize(corrupted_file)
                print(f"Image corrigée: {new_size} octets")
                
                # Vérifier que la correction a fonctionné
                if new_size > 0:
                    print("[OK] Image corrompue remplacée avec succès!")
                    
                    # Test de validation de l'image
                    try:
                        from PIL import Image
                        with Image.open(corrupted_file) as img:
                            print(f"[OK] Image valide: {img.format} {img.size}")
                    except Exception as e:
                        print(f"[ERROR] Image toujours corrompue: {e}")
                else:
                    print("[ERROR] La copie a échoué")
            else:
                print("[ERROR] L'image source est également vide")
        else:
            print(f"[ERROR] Image source non trouvée: {source_image}")

conn.close()

print("\n=== SOLUTION APPLIQUÉE ===")
print("L'image corrompue a été remplacée par l'image de test fonctionnelle.")
print("Actualisez la page de l'exercice pour voir le changement.")
