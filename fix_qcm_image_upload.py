import sqlite3
import json
import shutil
import os

# Corriger l'image QCM en remplaçant le fichier vide par une image valide
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Récupérer l'exercice QCM
cursor.execute('SELECT id, title, content, image_path FROM exercise WHERE id = 4')
result = cursor.fetchone()

if result:
    exercise_id, title, content_json, image_path = result
    print(f"Exercice trouvé: {title}")
    
    # Parser le contenu
    content = json.loads(content_json)
    current_image = content.get('image')
    print(f"Image actuelle: {current_image}")
    
    # Vérifier si le fichier image actuel existe et est vide
    if current_image:
        # Corriger le chemin - enlever le /static/ initial pour éviter static/static/
        if current_image.startswith('/static/'):
            current_file = current_image[1:]  # Enlever le / initial
        else:
            current_file = f"static/{current_image.lstrip('/')}"
        if os.path.exists(current_file):
            size = os.path.getsize(current_file)
            print(f"Fichier actuel: {current_file} ({size} octets)")
            
            if size == 0:
                print("Le fichier est vide, remplacement nécessaire")
                
                # Utiliser l'image de test que nous avons créée
                source_image = "static/uploads/qcm_digestive_system_test.png"
                if os.path.exists(source_image):
                    # Copier l'image de test vers le fichier vide
                    shutil.copy2(source_image, current_file)
                    new_size = os.path.getsize(current_file)
                    print(f"Image remplacée: {current_file} ({new_size} octets)")
                    
                    # Vérifier que la copie a réussi
                    if new_size > 0:
                        print("[OK] Correction réussie!")
                    else:
                        print("[ERROR] La copie a échoué")
                else:
                    print(f"[ERROR] Image source non trouvée: {source_image}")
            else:
                print("Le fichier n'est pas vide, pas de correction nécessaire")
        else:
            print(f"[ERROR] Fichier non trouvé: {current_file}")

conn.close()
