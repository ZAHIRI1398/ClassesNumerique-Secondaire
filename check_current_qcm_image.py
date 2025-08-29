import sqlite3
import json
import os

# Vérifier l'état actuel de l'image QCM
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Récupérer l'exercice QCM
cursor.execute('SELECT id, title, content, image_path FROM exercise WHERE id = 4')
result = cursor.fetchone()

if result:
    exercise_id, title, content_json, image_path = result
    print(f"=== EXERCICE QCM ID {exercise_id} ===")
    print(f"Titre: {title}")
    
    # Parser le contenu
    content = json.loads(content_json)
    current_image = content.get('image')
    print(f"Image dans contenu: {current_image}")
    print(f"Image_path colonne: {image_path}")
    
    # Vérifier le fichier image actuel
    if current_image and current_image.startswith('/static/'):
        current_file = current_image[1:]  # Enlever le / initial
        print(f"Chemin fichier: {current_file}")
        
        if os.path.exists(current_file):
            size = os.path.getsize(current_file)
            print(f"Taille fichier: {size} octets")
            
            if size == 0:
                print("PROBLÈME: Fichier vide détecté")
            else:
                # Vérifier si le fichier est une image valide
                try:
                    from PIL import Image
                    with Image.open(current_file) as img:
                        print(f"Image valide: {img.format} {img.size}")
                except Exception as e:
                    print(f"PROBLÈME: Image corrompue - {e}")
        else:
            print(f"PROBLÈME: Fichier non trouvé - {current_file}")

conn.close()

# Lister les derniers fichiers dans uploads
print("\n=== FICHIERS RÉCENTS DANS UPLOADS ===")
uploads_dir = "static/uploads"
if os.path.exists(uploads_dir):
    files = []
    for f in os.listdir(uploads_dir):
        if "145200_M3pzNU" in f:  # Le fichier mentionné dans l'URL
            path = os.path.join(uploads_dir, f)
            size = os.path.getsize(path)
            print(f"Fichier trouvé: {f} ({size} octets)")
            
            # Tester si c'est une image valide
            try:
                from PIL import Image
                with Image.open(path) as img:
                    print(f"  Format: {img.format}, Taille: {img.size}")
            except Exception as e:
                print(f"  ERREUR: {e}")
