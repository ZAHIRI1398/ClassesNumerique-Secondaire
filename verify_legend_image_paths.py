"""
Script de diagnostic pour vérifier la cohérence des chemins d'images dans les exercices de type légende.
Ce script vérifie que exercise.image_path et content['main_image'] sont cohérents.
"""

import os
import sys
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('verify_legend_image_paths')

# Créer une application Flask minimale pour accéder à la base de données
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Définir le modèle Exercise
class Exercise(db.Model):
    __tablename__ = 'exercise'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    
    def get_content(self):
        if self.content:
            try:
                return json.loads(self.content)
            except json.JSONDecodeError:
                return {}
        return {}

def normalize_path(path):
    """Normalise un chemin d'image pour comparaison"""
    if not path:
        return None
    
    # Nettoyer les chemins
    path = path.replace('\\', '/')
    
    # Assurer que le chemin commence par /static/ pour les chemins locaux
    if not path.startswith('http') and not path.startswith('/static/'):
        if path.startswith('static/'):
            path = f"/{path}"
        else:
            path = f"/static/uploads/{os.path.basename(path)}"
    
    return path

def check_image_exists(path):
    """Vérifie si l'image existe physiquement"""
    if not path:
        return False
    
    if path.startswith('http'):
        # Pour les URLs externes, on ne peut pas vérifier facilement
        return True
    
    # Enlever le préfixe /static/ pour obtenir le chemin relatif
    if path.startswith('/static/'):
        relative_path = path[8:]  # Enlever '/static/'
    else:
        relative_path = path
    
    # Vérifier si le fichier existe
    full_path = os.path.join('static', relative_path)
    exists = os.path.isfile(full_path)
    
    return exists

def verify_legend_image_paths():
    """Vérifie la cohérence des chemins d'images pour les exercices de type légende"""
    with app.app_context():
        legend_exercises = Exercise.query.filter_by(exercise_type='legend').all()
        
        logger.info(f"Trouvé {len(legend_exercises)} exercices de type légende")
        
        issues = []
        for exercise in legend_exercises:
            logger.info(f"Vérification de l'exercice #{exercise.id}: {exercise.title}")
            
            content = exercise.get_content()
            main_image = content.get('main_image')
            image_path = exercise.image_path
            
            # Normaliser les chemins pour comparaison
            norm_main_image = normalize_path(main_image) if main_image else None
            norm_image_path = normalize_path(image_path) if image_path else None
            
            # Vérifier la cohérence
            if not norm_main_image and not norm_image_path:
                issues.append({
                    'exercise_id': exercise.id,
                    'title': exercise.title,
                    'issue': 'Aucun chemin d\'image défini',
                    'main_image': main_image,
                    'image_path': image_path
                })
                logger.warning(f"Exercice #{exercise.id}: Aucun chemin d'image défini")
                continue
            
            if norm_main_image != norm_image_path:
                issues.append({
                    'exercise_id': exercise.id,
                    'title': exercise.title,
                    'issue': 'Incohérence entre main_image et image_path',
                    'main_image': main_image,
                    'image_path': image_path,
                    'norm_main_image': norm_main_image,
                    'norm_image_path': norm_image_path
                })
                logger.warning(f"Exercice #{exercise.id}: Incohérence entre main_image ({main_image}) et image_path ({image_path})")
            
            # Vérifier si l'image existe physiquement
            image_to_check = norm_main_image or norm_image_path
            if not check_image_exists(image_to_check):
                issues.append({
                    'exercise_id': exercise.id,
                    'title': exercise.title,
                    'issue': 'Image non trouvée sur le disque',
                    'path_checked': image_to_check
                })
                logger.warning(f"Exercice #{exercise.id}: Image non trouvée sur le disque: {image_to_check}")
        
        # Afficher un résumé
        if issues:
            logger.info(f"Trouvé {len(issues)} problèmes dans {len(legend_exercises)} exercices de type légende")
            for issue in issues:
                logger.info(f"Exercice #{issue['exercise_id']} ({issue['title']}): {issue['issue']}")
        else:
            logger.info("Aucun problème trouvé dans les exercices de type légende")
        
        return issues

if __name__ == "__main__":
    issues = verify_legend_image_paths()
    
    # Sauvegarder les résultats dans un fichier JSON
    with open('legend_image_issues.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Résultats sauvegardés dans legend_image_issues.json")
