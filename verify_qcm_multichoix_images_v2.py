import os
import sys
import json
import sqlite3
from pathlib import Path

# Chemin vers le répertoire du projet
project_dir = os.path.dirname(os.path.abspath(__file__))

# Chemin vers la base de données
db_path = os.path.join(project_dir, 'instance', 'app.db')

def verify_image_paths():
    """Vérifie les chemins d'images pour les exercices QCM Multichoix"""
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
    
    # Parcourir les exercices et vérifier les chemins d'images
    for exercise in exercises:
        exercise_id, title, content_json, image_path = exercise
        
        print(f"\nVérification de l'exercice #{exercise_id}: {title}")
        print(f"Chemin d'image actuel: {image_path}")
        
        if not image_path:
            print("Pas d'image associée à cet exercice")
            continue
        
        # Vérifier si l'image existe au chemin actuel
        current_path = os.path.join(project_dir, image_path.lstrip('/'))
        if os.path.exists(current_path):
            print(f"[OK] L'image existe au chemin actuel: {current_path}")
            print(f"   Taille du fichier: {os.path.getsize(current_path)} octets")
        else:
            print(f"[NON] L'image n'existe PAS au chemin actuel: {current_path}")
        
        # Vérifier le chemin d'image dans le contenu JSON
        try:
            content = json.loads(content_json)
            if isinstance(content, dict) and 'image' in content:
                json_image_path = content['image']
                print(f"Chemin d'image dans le contenu JSON: {json_image_path}")
                
                if json_image_path != image_path:
                    print(f"[ATTENTION] Le chemin d'image dans le contenu JSON est différent du chemin dans la table exercise")
                
                # Vérifier si l'image existe au chemin indiqué dans le JSON
                json_current_path = os.path.join(project_dir, json_image_path.lstrip('/'))
                if os.path.exists(json_current_path):
                    print(f"[OK] L'image existe au chemin indiqué dans le JSON: {json_current_path}")
                    print(f"   Taille du fichier: {os.path.getsize(json_current_path)} octets")
                else:
                    print(f"[NON] L'image n'existe PAS au chemin indiqué dans le JSON: {json_current_path}")
            else:
                print("Pas de chemin d'image dans le contenu JSON")
        except json.JSONDecodeError:
            print("Erreur de décodage JSON pour le contenu de l'exercice")
    
    # Fermer la connexion
    conn.close()
    
    print("\nVérification des chemins d'images terminée")

if __name__ == "__main__":
    print("Vérification des chemins d'images pour les exercices QCM Multichoix...")
    verify_image_paths()
