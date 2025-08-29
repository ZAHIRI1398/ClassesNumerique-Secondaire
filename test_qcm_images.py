import os
import sqlite3
import requests
from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user

# Configuration
DATABASE_PATH = 'instance/app.db'
BASE_URL = 'http://127.0.0.1:5000'

def test_qcm_images():
    """
    Script de test pour vérifier l'affichage des images QCM
    """
    print("=== Test d'affichage des images QCM ===")
    
    # 1. Connexion à la base de données
    print("\n1. Connexion à la base de données...")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        print("[OK] Connexion à la base de données réussie")
    except Exception as e:
        print(f"[ERREUR] Erreur de connexion à la base de données: {e}")
        return
    
    # 2. Récupération des exercices QCM
    print("\n2. Récupération des exercices QCM...")
    try:
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE exercise_type = 'qcm'")
        qcm_exercises = cursor.fetchall()
        print(f"[OK] {len(qcm_exercises)} exercices QCM trouvés")
        
        if not qcm_exercises:
            print("[ATTENTION] Aucun exercice QCM trouvé dans la base de données")
            return
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la récupération des exercices QCM: {e}")
        return
    
    # 3. Vérification des chemins d'images
    print("\n3. Vérification des chemins d'images...")
    for exercise_id, title, image_path in qcm_exercises:
        print(f"\nExercice #{exercise_id}: {title}")
        print(f"  Chemin d'image: {image_path}")
        
        # Vérifier si le chemin est défini
        if not image_path:
            print(f"  [ATTENTION] Pas de chemin d'image défini pour l'exercice #{exercise_id}")
            continue
        
        # Vérifier si le fichier existe physiquement
        if image_path.startswith('/static/'):
            local_path = image_path[8:]  # Enlever le préfixe '/static/'
            if os.path.exists(local_path):
                print(f"  [OK] Fichier image trouvé: {local_path}")
            else:
                print(f"  [ERREUR] Fichier image non trouvé: {local_path}")
                
                # Vérifier les chemins alternatifs
                alt_paths = [
                    f"static/uploads/qcm/{os.path.basename(image_path)}",
                    f"static/uploads/{os.path.basename(image_path)}",
                    f"static/uploads/exercises/{os.path.basename(image_path)}"
                ]
                
                found = False
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        print(f"  [OK] Fichier image trouvé dans un chemin alternatif: {alt_path}")
                        found = True
                        break
                
                if not found:
                    print(f"  [ERREUR] Fichier image non trouvé dans aucun chemin alternatif")
        
        # Tester l'accès à l'image via l'URL
        try:
            image_url = f"{BASE_URL}{image_path}"
            response = requests.head(image_url)
            if response.status_code == 200:
                print(f"  [OK] Image accessible via URL: {image_url}")
            else:
                print(f"  [ERREUR] Image non accessible via URL: {image_url} (status: {response.status_code})")
        except Exception as e:
            print(f"  [ERREUR] Erreur lors de l'accès à l'URL de l'image: {e}")
    
    # 4. Vérification des images dans le dossier /static/uploads/qcm/
    print("\n4. Vérification des images dans le dossier /static/uploads/qcm/...")
    qcm_upload_dir = "static/uploads/qcm"
    
    if os.path.exists(qcm_upload_dir):
        qcm_images = os.listdir(qcm_upload_dir)
        print(f"[OK] Dossier {qcm_upload_dir} trouvé avec {len(qcm_images)} images")
        
        # Afficher les 5 premières images
        for i, img in enumerate(qcm_images[:5]):
            print(f"  - {img}")
        if len(qcm_images) > 5:
            print(f"  - ... et {len(qcm_images) - 5} autres images")
    else:
        print(f"[ERREUR] Dossier {qcm_upload_dir} non trouvé")
    
    # 5. Conclusion
    print("\n5. Conclusion:")
    print("Test terminé. Vérifiez les résultats ci-dessus pour déterminer si les images QCM s'affichent correctement.")
    print("Pour une vérification visuelle complète, accédez à un exercice QCM via l'interface web.")

if __name__ == "__main__":
    test_qcm_images()
