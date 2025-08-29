import os
import sqlite3
import logging
from flask import Flask
import sys
import re
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Création d'une mini-application Flask pour utiliser current_app
app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

def associate_qcm_images():
    """
    Associe les images QCM présentes dans static/uploads/qcm/ aux exercices QCM
    dans la base de données qui n'ont pas d'image définie ou dont l'image n'est pas trouvée.
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
        
        # Récupération des images dans le dossier static/uploads/qcm/
        qcm_dir = os.path.join('static', 'uploads', 'qcm')
        if not os.path.exists(qcm_dir):
            logger.error(f"Dossier {qcm_dir} non trouvé")
            return
        
        qcm_images = [f for f in os.listdir(qcm_dir) if os.path.isfile(os.path.join(qcm_dir, f))]
        logger.info(f"Nombre d'images QCM trouvées: {len(qcm_images)}")
        
        # Création d'un backup de la base de données
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_db_path = f"instance/classe_numerique_backup_{backup_timestamp}.db"
        
        # Copie de la base de données
        with open(db_path, 'rb') as src, open(backup_db_path, 'wb') as dst:
            dst.write(src.read())
        
        logger.info(f"Backup de la base de données créé: {backup_db_path}")
        
        # Association des images aux exercices
        exercises_updated = 0
        
        for exercise in qcm_exercises:
            exercise_id, title, image_path, exercise_type = exercise
            
            # Vérifier si l'exercice a déjà une image valide
            has_valid_image = False
            if image_path:
                # Normaliser le chemin d'image (enlever /static/ si présent)
                normalized_path = image_path
                if normalized_path.startswith('/static/'):
                    normalized_path = normalized_path[8:]  # Enlever '/static/'
                
                # Vérifier si l'image existe
                if os.path.exists(os.path.join('static', normalized_path)) or os.path.exists(normalized_path):
                    has_valid_image = True
            
            if not has_valid_image:
                logger.info(f"Exercice {exercise_id} ({title}) n'a pas d'image valide")
                
                # Chercher une image correspondante par ID ou par titre
                matching_image = None
                
                # Essayer de trouver par ID
                id_pattern = re.compile(f".*_{exercise_id}[_.].*")
                for img in qcm_images:
                    if id_pattern.match(img):
                        matching_image = img
                        logger.info(f"Image trouvée par ID: {img}")
                        break
                
                # Si pas trouvé par ID, essayer par titre (simplifié)
                if not matching_image:
                    # Simplifier le titre pour la recherche
                    simple_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
                    if simple_title:  # Vérifier que le titre simplifié n'est pas vide
                        for img in qcm_images:
                            simple_img = re.sub(r'[^a-zA-Z0-9]', '', os.path.splitext(img)[0].lower())
                            if simple_title in simple_img or simple_img in simple_title:
                                matching_image = img
                                logger.info(f"Image trouvée par titre: {img}")
                                break
                
                # Si toujours pas trouvé, prendre la première image disponible
                if not matching_image and qcm_images:
                    # Trier les images par date (les plus récentes d'abord)
                    sorted_images = sorted(qcm_images, 
                                          key=lambda x: os.path.getmtime(os.path.join(qcm_dir, x)), 
                                          reverse=True)
                    
                    # Prendre la première image qui n'est pas déjà utilisée
                    for img in sorted_images:
                        cursor.execute("SELECT COUNT(*) FROM exercise WHERE image_path LIKE ?", (f'%{img}%',))
                        if cursor.fetchone()[0] == 0:
                            matching_image = img
                            logger.info(f"Image attribuée par défaut: {img}")
                            break
                
                # Mettre à jour l'exercice avec l'image trouvée
                if matching_image:
                    new_image_path = f"/static/uploads/qcm/{matching_image}"
                    cursor.execute("""
                        UPDATE exercise 
                        SET image_path = ? 
                        WHERE id = ?
                    """, (new_image_path, exercise_id))
                    
                    logger.info(f"✅ Exercice {exercise_id} mis à jour avec l'image: {new_image_path}")
                    exercises_updated += 1
                else:
                    logger.warning(f"❌ Aucune image trouvée pour l'exercice {exercise_id}")
        
        # Commit des changements
        conn.commit()
        logger.info(f"\nRésumé: {exercises_updated} exercices QCM mis à jour avec des images")
        
        # Vérification finale
        cursor.execute("""
            SELECT id, title, image_path
            FROM exercise
            WHERE exercise_type = 'qcm'
        """)
        updated_exercises = cursor.fetchall()
        
        logger.info("\nÉtat final des exercices QCM:")
        for ex in updated_exercises:
            ex_id, ex_title, ex_image = ex
            image_status = "✅" if ex_image and (
                os.path.exists(ex_image[1:] if ex_image.startswith('/') else ex_image) or 
                os.path.exists(os.path.join('static', ex_image[8:] if ex_image.startswith('/static/') else ex_image))
            ) else "❌"
            logger.info(f"{image_status} ID {ex_id}: {ex_title[:30]}... - {ex_image}")
        
        conn.close()
        logger.info("\nAssociation des images QCM terminée.")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'association des images QCM: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    with app.app_context():
        associate_qcm_images()
