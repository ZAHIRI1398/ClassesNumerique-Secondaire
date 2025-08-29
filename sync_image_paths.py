"""
Script pour synchroniser exercise.image_path avec content.main_image pour les exercices de type image_labeling.
"""

import os
import json
import sqlite3
import time

def sync_image_paths(db_path):
    """
    Synchronise exercise.image_path avec content.main_image pour tous les exercices de type image_labeling.
    
    Args:
        db_path (str): Chemin vers le fichier de base de données SQLite
    """
    if not os.path.exists(db_path):
        print(f"[ERREUR] Le fichier de base de données {db_path} n'existe pas.")
        return
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupérer tous les exercices de type image_labeling
    cursor.execute("SELECT * FROM exercise WHERE exercise_type = 'image_labeling'")
    exercises = cursor.fetchall()
    
    if not exercises:
        print("[INFO] Aucun exercice de type image_labeling trouvé.")
        conn.close()
        return
        
    print(f"[INFO] {len(exercises)} exercices de type image_labeling trouvés.")
    
    updated_count = 0
    
    for exercise in exercises:
        exercise_id = exercise['id']
        image_path = exercise['image_path']
        content_str = exercise['content']
        
        try:
            content = json.loads(content_str) if content_str else {}
            
            if 'main_image' in content and content['main_image']:
                main_image = content['main_image']
                
                # Si image_path est None ou différent de main_image, mettre à jour
                if image_path != main_image:
                    print(f"[INFO] Exercice ID {exercise_id}: Mise à jour de image_path")
                    print(f"  - Ancien: {image_path}")
                    print(f"  - Nouveau: {main_image}")
                    
                    # Mettre à jour image_path avec la valeur de main_image
                    cursor.execute(
                        "UPDATE exercise SET image_path = ? WHERE id = ?",
                        (main_image, exercise_id)
                    )
                    updated_count += 1
                else:
                    print(f"[INFO] Exercice ID {exercise_id}: image_path et main_image déjà synchronisés.")
            else:
                print(f"[AVERTISSEMENT] Exercice ID {exercise_id}: Aucun champ main_image dans le contenu JSON.")
        except json.JSONDecodeError:
            print(f"[ERREUR] Exercice ID {exercise_id}: Le contenu JSON n'est pas valide.")
    
    # Valider les modifications
    conn.commit()
    conn.close()
    
    print(f"[INFO] {updated_count} exercices mis à jour.")
    return updated_count

def main():
    """
    Fonction principale pour exécuter le script.
    """
    # Chemins possibles vers la base de données
    db_paths = [
        'instance/app.db',
        'instance/classe_numerique.db',
        'app.db',
        'classe_numerique.db'
    ]
    
    # Trouver le premier chemin valide
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("[ERREUR] Aucun fichier de base de données trouvé.")
        return
    
    print(f"[INFO] Utilisation de la base de données: {db_path}")
    
    # Créer une sauvegarde de la base de données
    backup_path = f"{db_path}.backup_{int(time.time())}"
    with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
        dst.write(src.read())
    print(f"[INFO] Sauvegarde de la base de données créée: {backup_path}")
    
    # Synchroniser les chemins d'images
    updated_count = sync_image_paths(db_path)
    
    if updated_count > 0:
        print(f"[SUCCÈS] {updated_count} exercices ont été mis à jour avec succès.")
    else:
        print("[INFO] Aucun exercice n'a été mis à jour.")

if __name__ == "__main__":
    main()
