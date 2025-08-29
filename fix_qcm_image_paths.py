"""
Script pour corriger les chemins d'images dans les exercices QCM
"""

from flask import Flask, current_app
from models import db, Exercise
import json
import os
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])
db.init_app(app)

# Créer le contexte d'application pour les opérations de base de données
app.app_context().push()

def fix_image_paths():
    """
    Corrige les chemins d'images dans les exercices QCM
    - Vérifie si les images existent dans le système de fichiers
    - Met à jour les chemins dans la base de données pour pointer vers les emplacements corrects
    """
    with app.app_context():
        # Récupérer tous les exercices QCM
        qcm_exercises = Exercise.query.filter_by(exercise_type='qcm').all()
        
        print(f"Trouvé {len(qcm_exercises)} exercices QCM")
        
        for exercise in qcm_exercises:
            try:
                # Analyser le contenu JSON
                content = json.loads(exercise.content) if exercise.content else {}
                
                # Vérifier si l'exercice a une image dans son contenu
                if 'image' in content and content['image']:
                    old_path = content['image']
                    
                    # Vérifier si le chemin commence par /static/exercises/
                    if old_path.startswith('/static/exercises/'):
                        filename = os.path.basename(old_path)
                        
                        # Vérifier si l'image existe dans /static/uploads/
                        uploads_path = f"/static/uploads/{filename}"
                        physical_path = os.path.join(app.root_path, 'static', 'uploads', filename)
                        
                        if os.path.exists(physical_path):
                            # Mettre à jour le chemin dans le contenu
                            content['image'] = uploads_path
                            exercise.content = json.dumps(content)
                            
                            # Mettre à jour également exercise.image_path si nécessaire
                            if exercise.image_path != uploads_path:
                                exercise.image_path = uploads_path
                                
                            print(f"Exercice {exercise.id}: Chemin mis à jour de {old_path} vers {uploads_path}")
                        else:
                            # Si l'image n'existe pas dans /static/uploads/, vérifier dans /static/exercises/
                            exercises_physical_path = os.path.join(app.root_path, 'static', 'exercises', filename)
                            
                            if os.path.exists(exercises_physical_path):
                                print(f"Exercice {exercise.id}: L'image existe dans /static/exercises/, pas besoin de mise à jour")
                            else:
                                print(f"Exercice {exercise.id}: ATTENTION - Image introuvable: {old_path}")
                    
                    # Vérifier si le chemin ne commence pas par /static/
                    elif not old_path.startswith('/static/'):
                        # Normaliser le chemin pour qu'il commence par /static/
                        filename = os.path.basename(old_path)
                        
                        # Vérifier si l'image existe dans /static/uploads/
                        uploads_path = f"/static/uploads/{filename}"
                        physical_path = os.path.join(app.root_path, 'static', 'uploads', filename)
                        
                        if os.path.exists(physical_path):
                            # Mettre à jour le chemin dans le contenu
                            content['image'] = uploads_path
                            exercise.content = json.dumps(content)
                            
                            # Mettre à jour également exercise.image_path si nécessaire
                            if exercise.image_path != uploads_path:
                                exercise.image_path = uploads_path
                                
                            print(f"Exercice {exercise.id}: Chemin normalisé de {old_path} vers {uploads_path}")
                        else:
                            print(f"Exercice {exercise.id}: ATTENTION - Image introuvable: {old_path}")
                
                # Vérifier si exercise.image_path existe mais pas content['image']
                elif exercise.image_path and not content.get('image'):
                    # Ajouter le chemin d'image au contenu
                    content['image'] = exercise.image_path
                    exercise.content = json.dumps(content)
                    print(f"Exercice {exercise.id}: Ajout de l'image {exercise.image_path} au contenu")
                
                # Vérifier si content['image'] existe mais pas exercise.image_path
                elif content.get('image') and not exercise.image_path:
                    exercise.image_path = content['image']
                    print(f"Exercice {exercise.id}: Ajout de l'image {content['image']} à exercise.image_path")
                    
                # Sauvegarder les modifications
                db.session.commit()
                
            except Exception as e:
                print(f"Erreur lors du traitement de l'exercice {exercise.id}: {str(e)}")
                db.session.rollback()
        
        print("Correction des chemins d'images terminée")

if __name__ == "__main__":
    fix_image_paths()
