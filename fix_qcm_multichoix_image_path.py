import os
import json
import sqlite3
import shutil
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DATABASE_PATH = 'instance/app.db'
BACKUP_DIR = f'static/backup_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

def ensure_directory_exists(directory):
    """Crée le répertoire s'il n'existe pas"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Répertoire créé: {directory}")

def backup_database():
    """Crée une sauvegarde de la base de données"""
    backup_path = f"instance/app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DATABASE_PATH, backup_path)
    logger.info(f"Base de données sauvegardée: {backup_path}")
    return backup_path

def fix_general_image_path():
    """Corrige le chemin de l'image general_20250829_212504_528d57cf.png"""
    # Chemins source et destination
    source_path = 'static/exercises/general/general_20250829_212504_528d57cf.png'
    target_dir = 'static/uploads/qcm_multichoix'
    target_path = f'{target_dir}/general_20250829_212504_528d57cf.png'
    
    # Vérifier si l'image source existe
    if not os.path.exists(source_path):
        logger.error(f"Image source introuvable: {source_path}")
        return False
    
    # Créer le répertoire cible s'il n'existe pas
    ensure_directory_exists(target_dir)
    
    # Copier l'image vers le répertoire cible
    try:
        shutil.copy2(source_path, target_path)
        logger.info(f"Image copiée avec succès: {source_path} -> {target_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la copie de l'image: {e}")
        return False

def update_database_path():
    """Met à jour le chemin de l'image dans la base de données"""
    # Sauvegarde de la base de données
    backup_path = backup_database()
    
    # Connexion à la base de données
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Rechercher les exercices avec le chemin d'image problématique
        problematic_path = '/static/uploads/qcm_multichoix/general_20250829_212504_528d57cf.png'
        cursor.execute("SELECT id, title, content, image_path FROM exercise WHERE image_path = ? OR content LIKE ?", 
                      (problematic_path, f'%{problematic_path}%'))
        
        exercises = cursor.fetchall()
        if not exercises:
            logger.warning("Aucun exercice avec le chemin d'image problématique n'a été trouvé.")
            return False
        
        # Traiter chaque exercice
        for exercise_id, title, content_json, image_path in exercises:
            logger.info(f"Traitement de l'exercice #{exercise_id}: {title}")
            
            # Mettre à jour le champ image_path si nécessaire
            if image_path == problematic_path:
                cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", 
                              ('/static/exercises/general/general_20250829_212504_528d57cf.png', exercise_id))
                logger.info(f"Chemin d'image mis à jour dans le champ image_path pour l'exercice #{exercise_id}")
            
            # Mettre à jour le champ content si nécessaire
            if content_json and problematic_path in content_json:
                try:
                    content = json.loads(content_json)
                    if 'image' in content and content['image'] == problematic_path:
                        content['image'] = '/static/exercises/general/general_20250829_212504_528d57cf.png'
                        cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", 
                                      (json.dumps(content), exercise_id))
                        logger.info(f"Chemin d'image mis à jour dans le champ content pour l'exercice #{exercise_id}")
                except json.JSONDecodeError:
                    logger.error(f"Contenu JSON invalide pour l'exercice #{exercise_id}")
        
        # Valider les modifications
        conn.commit()
        logger.info("Modifications enregistrées dans la base de données")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la base de données: {e}")
        return False
    
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def main():
    """Fonction principale"""
    print("=== Correction du chemin d'image QCM Multichoix ===\n")
    
    # 1. Copier l'image vers le répertoire cible
    if fix_general_image_path():
        print("[SUCCES] Image copiée avec succès vers le répertoire cible")
    else:
        print("[ERREUR] Échec de la copie de l'image")
    
    # 2. Mettre à jour la base de données
    if update_database_path():
        print("[SUCCES] Base de données mise à jour avec succès")
    else:
        print("[ERREUR] Échec de la mise à jour de la base de données")
    
    print("\nOpération terminée.")

if __name__ == "__main__":
    main()
