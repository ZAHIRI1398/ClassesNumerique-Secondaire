"""
Script de correction automatique pour les chemins d'images dans les exercices de type légende.
Ce script corrige les incohérences entre exercise.image_path et content['main_image'].
"""

import os
import sys
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import shutil
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fix_legend_image_paths.log')
    ]
)
logger = logging.getLogger('fix_legend_image_paths')

# Créer une application Flask minimale pour accéder à la base de données
app = Flask(__name__)

# Vérifier l'existence du répertoire instance et du fichier de base de données
instance_dir = os.path.join(os.getcwd(), 'instance')
db_path = os.path.join(instance_dir, 'app.db')

if not os.path.exists(instance_dir):
    os.makedirs(instance_dir, exist_ok=True)
    logger.warning(f"Le répertoire 'instance' n'existait pas et a été créé: {instance_dir}")

if not os.path.exists(db_path):
    logger.error(f"Le fichier de base de données n'existe pas: {db_path}")
    print(f"ERREUR: Le fichier de base de données n'existe pas: {db_path}")
    print("Vérifiez le chemin et assurez-vous que la base de données existe.")
    sys.exit(1)
else:
    logger.info(f"Base de données trouvée: {db_path}")

# Configurer SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
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
    """Normalise un chemin d'image pour le rendre compatible avec Flask"""
    if not path:
        return None
    
    # Nettoyer les chemins
    path = path.replace('\\', '/')
    
    # Extraire le nom du fichier
    filename = os.path.basename(path)
    
    # Construire le chemin normalisé
    if 'legend' in path.lower():
        normalized_path = f"/static/uploads/legend/{filename}"
    else:
        normalized_path = f"/static/uploads/{filename}"
    
    return normalized_path

def ensure_directory_exists(directory):
    """S'assure que le répertoire existe"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Répertoire créé: {directory}")

def copy_image_if_needed(old_path, new_path):
    """Copie l'image si nécessaire"""
    # Convertir les chemins web en chemins locaux
    if old_path.startswith('/static/'):
        old_local_path = old_path[8:]  # Enlever '/static/'
    else:
        old_local_path = old_path
    
    if new_path.startswith('/static/'):
        new_local_path = new_path[8:]  # Enlever '/static/'
    else:
        new_local_path = new_path
    
    # Chemins complets
    old_full_path = os.path.join('static', old_local_path)
    new_full_path = os.path.join('static', new_local_path)
    
    # Vérifier si l'ancienne image existe
    if os.path.isfile(old_full_path):
        # S'assurer que le répertoire de destination existe
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        
        # Copier l'image si elle n'existe pas déjà à la destination
        if not os.path.isfile(new_full_path):
            shutil.copy2(old_full_path, new_full_path)
            logger.info(f"Image copiée de {old_full_path} vers {new_full_path}")
        return True
    else:
        logger.warning(f"Image source non trouvée: {old_full_path}")
        return False

def fix_legend_image_paths():
    """Corrige les chemins d'images pour les exercices de type légende"""
    with app.app_context():
        # S'assurer que les répertoires nécessaires existent
        ensure_directory_exists('static/uploads')
        ensure_directory_exists('static/uploads/legend')
        
        # Créer un backup de la base de données
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backup_legend_fix_{timestamp}.db'
        try:
            shutil.copy2('instance/app.db', f'instance/{backup_file}')
            logger.info(f"Backup de la base de données créé: instance/{backup_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du backup: {str(e)}")
            return
        
        # Récupérer tous les exercices de type légende
        legend_exercises = Exercise.query.filter_by(exercise_type='legend').all()
        logger.info(f"Trouvé {len(legend_exercises)} exercices de type légende")
        
        fixed_count = 0
        for exercise in legend_exercises:
            logger.info(f"Traitement de l'exercice #{exercise.id}: {exercise.title}")
            
            content = exercise.get_content()
            main_image = content.get('main_image')
            image_path = exercise.image_path
            
            # Cas 1: Aucune image définie
            if not main_image and not image_path:
                logger.warning(f"Exercice #{exercise.id}: Aucune image définie, ignoré")
                continue
            
            # Cas 2: Seulement main_image est défini
            if main_image and not image_path:
                normalized_path = normalize_path(main_image)
                exercise.image_path = normalized_path
                content['main_image'] = normalized_path
                exercise.content = json.dumps(content)
                logger.info(f"Exercice #{exercise.id}: image_path défini à partir de main_image: {normalized_path}")
                fixed_count += 1
            
            # Cas 3: Seulement image_path est défini
            elif not main_image and image_path:
                normalized_path = normalize_path(image_path)
                exercise.image_path = normalized_path
                content['main_image'] = normalized_path
                exercise.content = json.dumps(content)
                logger.info(f"Exercice #{exercise.id}: main_image défini à partir de image_path: {normalized_path}")
                fixed_count += 1
            
            # Cas 4: Les deux sont définis mais différents
            elif main_image != image_path:
                # Préférer main_image car c'est celui utilisé dans le template
                normalized_path = normalize_path(main_image)
                
                # Copier l'image si nécessaire
                if image_path and main_image:
                    copy_image_if_needed(image_path, normalized_path)
                
                exercise.image_path = normalized_path
                content['main_image'] = normalized_path
                exercise.content = json.dumps(content)
                logger.info(f"Exercice #{exercise.id}: Synchronisation des chemins: {normalized_path}")
                fixed_count += 1
            
            # Cas 5: Les deux sont définis et identiques mais pas au format normalisé
            elif main_image == image_path:
                normalized_path = normalize_path(main_image)
                if normalized_path != main_image:
                    exercise.image_path = normalized_path
                    content['main_image'] = normalized_path
                    exercise.content = json.dumps(content)
                    logger.info(f"Exercice #{exercise.id}: Normalisation des chemins: {normalized_path}")
                    fixed_count += 1
        
        # Sauvegarder les modifications
        if fixed_count > 0:
            try:
                db.session.commit()
                logger.info(f"Modifications sauvegardées en base de données: {fixed_count} exercices corrigés")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
        else:
            logger.info("Aucune correction nécessaire")
        
        return fixed_count

if __name__ == "__main__":
    fixed_count = fix_legend_image_paths()
    
    if fixed_count is not None:
        logger.info(f"Correction terminée: {fixed_count} exercices corrigés")
        print(f"Correction terminée: {fixed_count} exercices corrigés")
        print(f"Consultez le fichier fix_legend_image_paths.log pour plus de détails")
    else:
        logger.error("Erreur lors de la correction")
        print("Erreur lors de la correction. Consultez le fichier fix_legend_image_paths.log pour plus de détails")
