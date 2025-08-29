import os
import sys
import json
import sqlite3
from pathlib import Path

# Chemin vers le répertoire du projet
project_dir = os.path.dirname(os.path.abspath(__file__))

# Chemin vers la base de données
db_path = os.path.join(project_dir, 'instance', 'app.db')

# Chemins alternatifs pour rechercher les images
alt_paths = [
    os.path.join(project_dir, 'static', 'uploads', 'qcm_multichoix'),
    os.path.join(project_dir, 'static', 'exercises', 'general'),
    os.path.join(project_dir, 'static', 'uploads'),
    os.path.join(project_dir, 'static', 'exercises', 'qcm'),
    os.path.join(project_dir, 'static', 'exercises'),
    os.path.join(project_dir, 'static', 'exercises', 'qcm_multichoix'),
    os.path.join(project_dir, 'static', 'exercises', 'qcm-multichoix')
]

def find_image_file(filename):
    """Recherche un fichier image dans les chemins alternatifs"""
    for alt_path in alt_paths:
        full_path = os.path.join(alt_path, filename)
        if os.path.exists(full_path):
            return full_path
    
    # Essayer avec des variations de casse
    for alt_path in alt_paths:
        # Lister tous les fichiers dans le répertoire
        if os.path.exists(alt_path):
            for file in os.listdir(alt_path):
                if file.lower() == filename.lower():
                    return os.path.join(alt_path, file)
    
    return None

def fix_image_paths():
    """Corrige les chemins d'images pour les exercices QCM Multichoix"""
    # Vérifier si la base de données existe
    if not os.path.exists(db_path):
        print(f"Base de données non trouvée: {db_path}")
        return
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Récupérer tous les exercices QCM Multichoix
    cursor.execute("SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm_multichoix'")
    exercises = cursor.fetchall()
    
    print(f"Nombre d'exercices QCM Multichoix trouvés: {len(exercises)}")
    
    # Créer les répertoires s'ils n'existent pas
    for path in alt_paths:
        os.makedirs(path, exist_ok=True)
    
    # Parcourir les exercices et corriger les chemins d'images
    for exercise in exercises:
        exercise_id, title, content_json, image_path = exercise
        
        print(f"\nTraitement de l'exercice #{exercise_id}: {title}")
        print(f"Chemin d'image actuel: {image_path}")
        
        if not image_path:
            print("Pas d'image associée à cet exercice")
            continue
        
        # Extraire le nom du fichier
        filename = os.path.basename(image_path)
        
        # Vérifier si l'image existe au chemin actuel
        current_path = os.path.join(project_dir, image_path.lstrip('/'))
        if os.path.exists(current_path):
            print(f"L'image existe au chemin actuel: {current_path}")
            continue
        
        # Rechercher l'image dans les chemins alternatifs
        found_path = find_image_file(filename)
        if found_path:
            # Convertir le chemin absolu en chemin relatif pour la base de données
            rel_path = '/' + os.path.relpath(found_path, project_dir).replace('\\', '/')
            print(f"Image trouvée à: {found_path}")
            print(f"Nouveau chemin relatif: {rel_path}")
            
            # Mettre à jour le chemin d'image dans la base de données
            cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", (rel_path, exercise_id))
            
            # Mettre à jour le chemin d'image dans le contenu JSON si nécessaire
            try:
                content = json.loads(content_json)
                if isinstance(content, dict) and 'image' in content:
                    content['image'] = rel_path
                    cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", 
                                 (json.dumps(content), exercise_id))
                    print("Chemin d'image mis à jour dans le contenu JSON")
            except json.JSONDecodeError:
                print("Erreur de décodage JSON pour le contenu de l'exercice")
            
            print(f"Chemin d'image mis à jour dans la base de données: {rel_path}")
        else:
            print(f"Image introuvable pour le fichier: {filename}")
            
            # Vérifier si l'image existe dans un autre format (png, jpg, jpeg, etc.)
            base_name = os.path.splitext(filename)[0]
            for ext in ['.png', '.jpg', '.jpeg', '.gif']:
                alt_filename = base_name + ext
                found_path = find_image_file(alt_filename)
                if found_path:
                    rel_path = '/' + os.path.relpath(found_path, project_dir).replace('\\', '/')
                    print(f"Image trouvée avec une extension différente: {found_path}")
                    print(f"Nouveau chemin relatif: {rel_path}")
                    
                    # Mettre à jour le chemin d'image dans la base de données
                    cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", (rel_path, exercise_id))
                    
                    # Mettre à jour le chemin d'image dans le contenu JSON si nécessaire
                    try:
                        content = json.loads(content_json)
                        if isinstance(content, dict) and 'image' in content:
                            content['image'] = rel_path
                            cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", 
                                         (json.dumps(content), exercise_id))
                            print("Chemin d'image mis à jour dans le contenu JSON")
                    except json.JSONDecodeError:
                        print("Erreur de décodage JSON pour le contenu de l'exercice")
                    
                    print(f"Chemin d'image mis à jour dans la base de données: {rel_path}")
                    break
            else:
                print("Aucune image alternative trouvée")
    
    # Valider les modifications
    conn.commit()
    
    # Fermer la connexion
    conn.close()
    
    print("\nCorrection des chemins d'images terminée")

if __name__ == "__main__":
    print("Correction des chemins d'images pour les exercices QCM Multichoix...")
    fix_image_paths()
