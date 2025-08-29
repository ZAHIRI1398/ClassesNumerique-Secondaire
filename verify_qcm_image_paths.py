import os
import sqlite3
import logging
from flask import Flask, current_app
import sys
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Création d'une mini-application Flask pour utiliser current_app
app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

def verify_qcm_image_paths():
    """
    Vérifie les chemins d'images pour les exercices QCM et analyse pourquoi 
    certaines images ne s'affichent pas malgré leur présence dans le système de fichiers.
    """
    try:
        # Connexion à la base de données
        db_path = os.path.join('instance', 'classe_numerique.db')
        if not os.path.exists(db_path):
            logger.error(f"Base de données non trouvée: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupération des exercices QCM
        cursor.execute("""
            SELECT id, title, image_path, exercise_type
            FROM exercise
            WHERE exercise_type = 'qcm'
        """)
        qcm_exercises = cursor.fetchall()
        
        logger.info(f"Nombre d'exercices QCM trouvés: {len(qcm_exercises)}")
        
        # Vérification des chemins d'images
        for exercise in qcm_exercises:
            exercise_id, title, image_path, exercise_type = exercise
            logger.info(f"\nExercice ID {exercise_id}: {title}")
            logger.info(f"Chemin d'image enregistré: {image_path}")
            
            # Vérifier si le chemin est None ou vide
            if not image_path:
                logger.warning(f"Exercice {exercise_id}: Pas de chemin d'image défini")
                continue
            
            # Normaliser le chemin d'image (enlever /static/ si présent)
            normalized_path = image_path
            if normalized_path.startswith('/static/'):
                normalized_path = normalized_path[8:]  # Enlever '/static/'
            
            # Chemins possibles à vérifier
            possible_paths = [
                os.path.join('static', normalized_path),
                normalized_path,
                image_path,
                os.path.join('static', 'uploads', 'qcm', os.path.basename(normalized_path)),
                os.path.join('static', 'uploads', os.path.basename(normalized_path)),
            ]
            
            # Vérifier l'existence des fichiers
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    logger.info(f"✅ Image trouvée: {path}")
                    logger.info(f"   Taille: {os.path.getsize(path)} octets")
                    found = True
                    break
            
            if not found:
                logger.error(f"❌ Image non trouvée pour l'exercice {exercise_id}")
                logger.error(f"   Chemins vérifiés: {possible_paths}")
                
                # Recherche d'images similaires
                base_name = os.path.basename(normalized_path)
                logger.info(f"Recherche d'images similaires à: {base_name}")
                
                # Recherche dans les dossiers potentiels
                search_dirs = [
                    os.path.join('static', 'uploads'),
                    os.path.join('static', 'uploads', 'qcm'),
                    os.path.join('static', 'uploads', 'exercises'),
                    os.path.join('static', 'uploads', 'exercises', 'qcm'),
                ]
                
                for search_dir in search_dirs:
                    if os.path.exists(search_dir):
                        logger.info(f"Recherche dans: {search_dir}")
                        files = os.listdir(search_dir)
                        for file in files:
                            if base_name.lower() in file.lower():
                                logger.info(f"   Image similaire trouvée: {os.path.join(search_dir, file)}")
        
        # Vérifier les fichiers dans le dossier uploads/qcm
        qcm_dir = os.path.join('static', 'uploads', 'qcm')
        if os.path.exists(qcm_dir):
            logger.info(f"\nFichiers dans {qcm_dir}:")
            files = os.listdir(qcm_dir)
            for file in files:
                file_path = os.path.join(qcm_dir, file)
                logger.info(f"- {file} ({os.path.getsize(file_path)} octets)")
                
                # Vérifier si ce fichier est référencé dans la base de données
                cursor.execute("""
                    SELECT id, title FROM exercise 
                    WHERE image_path LIKE ? OR image_path LIKE ?
                """, (f'%{file}%', f'%{os.path.splitext(file)[0]}%'))
                references = cursor.fetchall()
                
                if references:
                    logger.info(f"   Référencé par: {references}")
                else:
                    logger.warning(f"   ⚠️ Non référencé dans la base de données")
        else:
            logger.warning(f"Le dossier {qcm_dir} n'existe pas")
        
        # Vérifier les permissions des dossiers
        logger.info("\nVérification des permissions des dossiers:")
        dirs_to_check = [
            'static',
            os.path.join('static', 'uploads'),
            os.path.join('static', 'uploads', 'qcm'),
        ]
        
        for dir_path in dirs_to_check:
            if os.path.exists(dir_path):
                try:
                    # Vérifier si le dossier est accessible en lecture
                    test_file = os.listdir(dir_path)
                    logger.info(f"✅ {dir_path}: Accessible en lecture")
                except Exception as e:
                    logger.error(f"❌ {dir_path}: Erreur d'accès - {str(e)}")
            else:
                logger.warning(f"⚠️ {dir_path}: N'existe pas")
        
        conn.close()
        logger.info("\nVérification terminée.")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des chemins d'images: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    with app.app_context():
        verify_qcm_image_paths()
