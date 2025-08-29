import sqlite3
import json
import shutil
import os

# Corriger la dernière image QCM vide
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
    print(f"Image actuelle: {current_image}")
    
    # Vérifier le fichier image
    if current_image and current_image.startswith('/static/'):
        current_file = current_image[1:]  # Enlever le / initial
        print(f"Chemin fichier: {current_file}")
        
        if os.path.exists(current_file):
            size = os.path.getsize(current_file)
            print(f"Taille fichier: {size} octets")
            
            if size == 0:
                print("Fichier vide détecté - correction en cours...")
                
                # Utiliser l'image de test fonctionnelle
                source_image = "static/uploads/qcm_digestive_system_test.png"
                if os.path.exists(source_image):
                    # Copier l'image de test vers le fichier vide
                    shutil.copy2(source_image, current_file)
                    new_size = os.path.getsize(current_file)
                    print(f"Image corrigée: {new_size} octets")
                    
                    if new_size > 0:
                        print("[OK] Correction réussie!")
                        
                        # Vérifier que l'image est accessible via HTTP
                        import requests
                        try:
                            response = requests.get(f"http://127.0.0.1:5000{current_image}")
                            print(f"Test HTTP: {response.status_code} ({len(response.content)} octets)")
                        except Exception as e:
                            print(f"Erreur test HTTP: {e}")
                    else:
                        print("[ERROR] Échec de la copie")
                else:
                    print(f"[ERROR] Image source non trouvée: {source_image}")
            else:
                print("Fichier non vide - pas de correction nécessaire")
        else:
            print(f"[ERROR] Fichier non trouvé: {current_file}")

conn.close()
