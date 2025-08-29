"""
Script pour vérifier le chemin d'image dans l'exercice QCM #23
"""

from flask import Flask
from models import db, Exercise
import json
import os
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])
db.init_app(app)

# Créer le contexte d'application pour les opérations de base de données
app.app_context().push()

def verify_image_path():
    """
    Vérifie que le chemin d'image pour l'exercice QCM #23 est correct
    et que l'image existe physiquement
    """
    # Récupérer l'exercice #23
    exercise = Exercise.query.get(23)
    
    if not exercise:
        print("Exercice #23 non trouvé")
        return
    
    print(f"Exercice trouvé: {exercise.title} (ID: {exercise.id})")
    print(f"Type d'exercice: {exercise.exercise_type}")
    
    # Vérifier le chemin d'image dans exercise.image_path
    print(f"Chemin d'image (exercise.image_path): {exercise.image_path}")
    
    # Vérifier le chemin d'image dans le contenu JSON
    content = json.loads(exercise.content) if exercise.content else {}
    content_image = content.get('image')
    print(f"Chemin d'image (content.image): {content_image}")
    
    # Vérifier si les chemins correspondent
    if exercise.image_path == content_image:
        print("[OK] Les chemins d'image sont synchronises")
    else:
        print("[ERREUR] Les chemins d'image ne sont pas synchronises")
    
    # Vérifier si l'image existe physiquement
    if exercise.image_path:
        # Enlever le préfixe '/static/' pour obtenir le chemin relatif
        relative_path = exercise.image_path.replace('/static/', '', 1)
        physical_path = os.path.join(app.root_path, 'static', *relative_path.split('/'))
        
        if os.path.exists(physical_path):
            print(f"[OK] L'image existe physiquement: {physical_path}")
        else:
            print(f"[ERREUR] L'image n'existe PAS physiquement: {physical_path}")
    
    # Vérifier si l'ancienne image existe encore
    old_path = '/static/exercises/1756168827_5cwjd8.png'
    relative_old_path = old_path.replace('/static/', '', 1)
    physical_old_path = os.path.join(app.root_path, 'static', *relative_old_path.split('/'))
    
    if os.path.exists(physical_old_path):
        print(f"[ATTENTION] L'ancienne image existe encore: {physical_old_path}")
    else:
        print(f"[OK] L'ancienne image n'existe plus: {physical_old_path}")

if __name__ == "__main__":
    verify_image_path()
