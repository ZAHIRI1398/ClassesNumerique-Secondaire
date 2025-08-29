"""
Script pour vérifier le chemin d'image d'un exercice spécifique dans la base de données.
"""

import os
import json
import sqlite3

def check_exercise_image_path(db_path, exercise_id=None):
    """
    Vérifie le chemin d'image d'un exercice spécifique ou de tous les exercices de type image_labeling.
    
    Args:
        db_path (str): Chemin vers le fichier de base de données SQLite
        exercise_id (int, optional): ID de l'exercice à vérifier. Si None, vérifie tous les exercices de type image_labeling.
    """
    if not os.path.exists(db_path):
        print(f"[ERREUR] Le fichier de base de données {db_path} n'existe pas.")
        return
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if exercise_id:
        # Vérifier un exercice spécifique
        cursor.execute("SELECT * FROM exercise WHERE id = ?", (exercise_id,))
        exercise = cursor.fetchone()
        
        if not exercise:
            print(f"[ERREUR] Aucun exercice trouvé avec l'ID {exercise_id}.")
            conn.close()
            return
            
        check_exercise(exercise)
    else:
        # Vérifier tous les exercices de type image_labeling
        cursor.execute("SELECT * FROM exercise WHERE exercise_type = 'image_labeling' ORDER BY id DESC")
        exercises = cursor.fetchall()
        
        if not exercises:
            print("[INFO] Aucun exercice de type image_labeling trouvé.")
            conn.close()
            return
            
        print(f"[INFO] {len(exercises)} exercices de type image_labeling trouvés.")
        
        for exercise in exercises:
            check_exercise(exercise)
    
    conn.close()

def check_exercise(exercise):
    """
    Vérifie et affiche les informations sur le chemin d'image d'un exercice.
    
    Args:
        exercise (sqlite3.Row): Ligne de la base de données représentant un exercice
    """
    exercise_id = exercise['id']
    exercise_type = exercise['exercise_type']
    image_path = exercise['image_path']
    content_str = exercise['content']
    
    print(f"\n[INFO] Exercice ID: {exercise_id}, Type: {exercise_type}")
    print(f"[INFO] image_path: {image_path}")
    
    # Vérifier si le fichier image existe
    if image_path:
        # Supprimer le préfixe /static/ pour obtenir le chemin relatif
        relative_path = image_path.replace('/static/', '') if image_path.startswith('/static/') else image_path
        file_path = os.path.join('static', relative_path) if not relative_path.startswith('static/') else relative_path
        
        if os.path.exists(file_path):
            print(f"[OK] Le fichier image existe: {file_path}")
        else:
            print(f"[ERREUR] Le fichier image n'existe pas: {file_path}")
    else:
        print("[AVERTISSEMENT] Aucun chemin d'image défini pour cet exercice.")
    
    # Vérifier le contenu JSON
    try:
        content = json.loads(content_str) if content_str else {}
        
        if 'main_image' in content:
            main_image = content['main_image']
            print(f"[INFO] content.main_image: {main_image}")
            
            # Vérifier si le fichier main_image existe
            if main_image:
                # Supprimer le préfixe /static/ pour obtenir le chemin relatif
                relative_path = main_image.replace('/static/', '') if main_image.startswith('/static/') else main_image
                file_path = os.path.join('static', relative_path) if not relative_path.startswith('static/') else relative_path
                
                if os.path.exists(file_path):
                    print(f"[OK] Le fichier main_image existe: {file_path}")
                else:
                    print(f"[ERREUR] Le fichier main_image n'existe pas: {file_path}")
        else:
            print("[AVERTISSEMENT] Aucun champ main_image dans le contenu JSON.")
            
        # Vérifier la cohérence entre image_path et main_image
        if image_path and 'main_image' in content and content['main_image']:
            if image_path == content['main_image']:
                print("[OK] image_path et main_image sont synchronisés.")
            else:
                print(f"[AVERTISSEMENT] image_path et main_image ne sont pas synchronisés.")
    except json.JSONDecodeError:
        print("[ERREUR] Le contenu JSON n'est pas valide.")

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
    
    # Vérifier automatiquement tous les exercices de type image_labeling
    print("[INFO] Vérification de tous les exercices de type image_labeling...")
    check_exercise_image_path(db_path)

if __name__ == "__main__":
    main()
