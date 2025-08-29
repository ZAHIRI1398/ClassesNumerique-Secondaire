from flask import Flask, render_template_string, jsonify
import os
import sys
from sqlalchemy import create_engine, text
import json

# Chemin vers le répertoire du projet
project_dir = os.path.dirname(os.path.abspath(__file__))

# Configuration de la base de données
db_path = os.path.join(project_dir, 'instance', 'app.db')
db_uri = f'sqlite:///{db_path}'

# Création d'une connexion à la base de données
engine = create_engine(db_uri)

def fix_qcm_multichoix_image_paths():
    """
    Corrige les chemins d'images des exercices QCM Multichoix dans la base de données
    """
    print("=== CORRECTION DES CHEMINS D'IMAGES QCM MULTICHOIX ===")
    
    # Récupérer tous les exercices QCM Multichoix
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm_multichoix'"))
        exercises = []
        for row in result:
            exercises.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'image_path': row[3]
            })
    
    if not exercises:
        print("[ERREUR] Aucun exercice QCM Multichoix trouvé dans la base de données.")
        return
    
    print(f"[INFO] {len(exercises)} exercice(s) QCM Multichoix trouvé(s).")
    
    # Analyser et corriger chaque exercice
    for exercise in exercises:
        print(f"\n--- Exercice #{exercise['id']}: {exercise['title']} ---")
        
        # Vérifier le chemin d'image
        image_path = exercise['image_path']
        if not image_path:
            print("[INFO] Pas d'image associée à cet exercice.")
            continue
        
        print(f"[INFO] Chemin d'image actuel: {image_path}")
        
        # Vérifier si le fichier existe au chemin indiqué
        full_path = os.path.join(project_dir, image_path.lstrip('/'))
        if os.path.exists(full_path):
            print(f"[OK] L'image existe au chemin indiqué: {full_path}")
            continue
        else:
            print(f"[ERREUR] L'image n'existe PAS au chemin indiqué: {full_path}")
            
            # Essayer de trouver l'image dans des chemins alternatifs
            filename = os.path.basename(image_path)
            alt_paths = [
                os.path.join('static', 'exercises', 'general', filename),
                os.path.join('static', 'uploads', filename),
                os.path.join('static', 'exercises', 'qcm', filename),
                os.path.join('static', 'exercises', filename)
            ]
            
            correct_path = None
            for alt_path in alt_paths:
                full_alt_path = os.path.join(project_dir, alt_path)
                if os.path.exists(full_alt_path):
                    print(f"[OK] Image trouvée dans un chemin alternatif: {full_alt_path}")
                    correct_path = f"/{alt_path.replace(os.sep, '/')}"
                    print(f"[INFO] Nouveau chemin relatif: {correct_path}")
                    break
            
            if correct_path:
                # Mettre à jour le chemin d'image dans la base de données
                try:
                    with engine.connect() as conn:
                        conn.execute(text(f"UPDATE exercise SET image_path = :path WHERE id = :id"), 
                                    {"path": correct_path, "id": exercise['id']})
                        conn.commit()
                        print(f"[OK] Chemin d'image mis à jour en base de données pour l'exercice #{exercise['id']}")
                    
                    # Mettre à jour le chemin d'image dans le contenu JSON si nécessaire
                    try:
                        content = json.loads(exercise['content'])
                        if 'image' in content:
                            old_json_path = content['image']
                            print(f"[INFO] Ancien chemin dans le contenu JSON: {old_json_path}")
                            content['image'] = correct_path
                            
                            # Mettre à jour le contenu JSON dans la base de données
                            with engine.connect() as conn:
                                conn.execute(text(f"UPDATE exercise SET content = :content WHERE id = :id"), 
                                           {"content": json.dumps(content), "id": exercise['id']})
                                conn.commit()
                                print(f"[OK] Contenu JSON mis à jour pour l'exercice #{exercise['id']}")
                    except json.JSONDecodeError:
                        print("[ERREUR] Contenu JSON invalide, impossible de mettre à jour le chemin d'image")
                except Exception as e:
                    print(f"[ERREUR] Erreur lors de la mise à jour en base de données: {str(e)}")
            else:
                print("[ERREUR] Image introuvable dans tous les chemins alternatifs.")
    
    print("\n=== FIN DE LA CORRECTION ===")

if __name__ == "__main__":
    fix_qcm_multichoix_image_paths()
