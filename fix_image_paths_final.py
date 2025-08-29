import sqlite3
import json
import os
import shutil

# Script pour corriger les chemins d'images de uploads vers exercises
def fix_image_paths():
    print("=== CORRECTION DES CHEMINS D'IMAGES ===")
    
    # Connexion à la base de données
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    
    # Récupérer tous les exercices avec des images
    cursor.execute('SELECT id, title, content, image_path FROM exercise WHERE content LIKE "%image%" OR image_path IS NOT NULL')
    exercises = cursor.fetchall()
    
    updated_count = 0
    
    for exercise_id, title, content_json, image_path in exercises:
        try:
            content = json.loads(content_json) if content_json else {}
            updated = False
            
            # Corriger l'image dans le contenu JSON
            if 'image' in content and content['image']:
                old_path = content['image']
                if '/static/uploads/' in old_path:
                    # Extraire le nom de fichier
                    filename = os.path.basename(old_path)
                    new_path = f"/static/exercises/{filename}"
                    content['image'] = new_path
                    updated = True
                    print(f"Exercice {exercise_id}: {old_path} -> {new_path}")
            
            # Corriger l'image_path
            new_image_path = image_path
            if image_path and '/static/uploads/' in image_path:
                filename = os.path.basename(image_path)
                new_image_path = f"/static/exercises/{filename}"
                updated = True
                print(f"Exercice {exercise_id} image_path: {image_path} -> {new_image_path}")
            
            # Mettre à jour la base de données si nécessaire
            if updated:
                cursor.execute(
                    'UPDATE exercise SET content = ?, image_path = ? WHERE id = ?',
                    (json.dumps(content), new_image_path, exercise_id)
                )
                updated_count += 1
                
        except Exception as e:
            print(f"Erreur exercice {exercise_id}: {e}")
    
    # Sauvegarder les changements
    conn.commit()
    conn.close()
    
    print(f"\n=== RÉSULTATS ===")
    print(f"Exercices traités: {len(exercises)}")
    print(f"Exercices mis à jour: {updated_count}")

def move_valid_images():
    """Déplacer les images valides de uploads vers exercises"""
    print("\n=== DÉPLACEMENT DES IMAGES VALIDES ===")
    
    uploads_dir = "static/uploads"
    exercises_dir = "static/exercises"
    
    if not os.path.exists(uploads_dir):
        print("Dossier uploads non trouvé")
        return
    
    os.makedirs(exercises_dir, exist_ok=True)
    moved_count = 0
    
    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            src_path = os.path.join(uploads_dir, filename)
            dst_path = os.path.join(exercises_dir, filename)
            
            # Vérifier si l'image est valide (taille > 0)
            if os.path.getsize(src_path) > 0:
                try:
                    # Déplacer seulement si le fichier n'existe pas déjà dans exercises
                    if not os.path.exists(dst_path):
                        shutil.move(src_path, dst_path)
                        print(f"Déplacé: {filename}")
                        moved_count += 1
                    else:
                        print(f"Existe déjà: {filename}")
                except Exception as e:
                    print(f"Erreur déplacement {filename}: {e}")
            else:
                print(f"Image vide ignorée: {filename}")
    
    print(f"Images déplacées: {moved_count}")

if __name__ == "__main__":
    move_valid_images()
    fix_image_paths()
    print("\n=== CORRECTION TERMINÉE ===")
    print("Redémarrez Flask pour que les changements prennent effet.")
