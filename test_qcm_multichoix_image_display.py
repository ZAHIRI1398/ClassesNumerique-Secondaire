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

def test_qcm_multichoix_images():
    """
    Test de diagnostic pour les images des exercices QCM Multichoix
    """
    print("=== DIAGNOSTIC DES IMAGES QCM MULTICHOIX ===")
    
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
    
    print(f"[OK] {len(exercises)} exercice(s) QCM Multichoix trouvé(s).")
    
    # Analyser chaque exercice
    for exercise in exercises:
        print(f"\n--- Exercice #{exercise['id']}: {exercise['title']} ---")
        
        # Vérifier le chemin d'image
        image_path = exercise['image_path']
        if not image_path:
            print("[ERREUR] Pas d'image associée à cet exercice.")
            continue
        
        print(f"[INFO] Chemin d'image en base de données: {image_path}")
        
        # Vérifier si le fichier existe au chemin indiqué
        full_path = os.path.join(project_dir, image_path.lstrip('/'))
        if os.path.exists(full_path):
            print(f"[OK] L'image existe au chemin indiqué: {full_path}")
        else:
            print(f"[ERREUR] L'image n'existe PAS au chemin indiqué: {full_path}")
            
            # Essayer de trouver l'image dans des chemins alternatifs
            filename = os.path.basename(image_path)
            alt_paths = [
                os.path.join('static', 'uploads', 'qcm_multichoix', filename),
                os.path.join('static', 'uploads', filename),
                os.path.join('static', 'exercises', 'general', filename),
                os.path.join('static', 'exercises', 'qcm', filename),
                os.path.join('static', 'exercises', filename)
            ]
            
            found = False
            for alt_path in alt_paths:
                full_alt_path = os.path.join(project_dir, alt_path)
                if os.path.exists(full_alt_path):
                    print(f"[OK] Image trouvée dans un chemin alternatif: {full_alt_path}")
                    print(f"[INFO] Chemin relatif correct: /{alt_path}")
                    found = True
                    break
            
            if not found:
                print("[ERREUR] Image introuvable dans tous les chemins alternatifs.")
        
        # Vérifier le contenu JSON
        try:
            content = json.loads(exercise['content'])
            print(f"[OK] Contenu JSON valide avec {len(content.get('questions', []))} question(s)")
            
            # Vérifier si le contenu contient une référence à l'image
            if 'image' in content:
                print(f"[INFO] Chemin d'image dans le contenu JSON: {content['image']}")
                
                # Vérifier si ce chemin existe
                content_image_path = os.path.join(project_dir, content['image'].lstrip('/'))
                if os.path.exists(content_image_path):
                    print(f"[OK] L'image référencée dans le contenu existe: {content_image_path}")
                else:
                    print(f"[ERREUR] L'image référencée dans le contenu N'EXISTE PAS: {content_image_path}")
        except json.JSONDecodeError:
            print("[ERREUR] Contenu JSON invalide")
    
    print("\n=== FIN DU DIAGNOSTIC ===")

if __name__ == "__main__":
    test_qcm_multichoix_images()
