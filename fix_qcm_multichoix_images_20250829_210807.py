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

# Chemins alternatifs pour rechercher les images QCM Multichoix
ALTERNATIVE_PATHS = [
    'static/exercises/qcm_multichoix/',
    'static/uploads/qcm_multichoix/',
    'static/uploads/exercises/qcm_multichoix/',
    'static/uploads/',
    'static/exercises/'
]

def ensure_directory_exists(directory):
    # Crée le répertoire s'il n'existe pas
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Répertoire créé: {directory}")

def backup_database():
    # Crée une sauvegarde de la base de données
    backup_path = f"instance/app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DATABASE_PATH, backup_path)
    logger.info(f"Base de données sauvegardée: {backup_path}")
    return backup_path

def find_image_in_alternative_paths(filename):
    # Recherche l'image dans les chemins alternatifs
    for path in ALTERNATIVE_PATHS:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path):
            return full_path
    return None

def fix_qcm_multichoix_images():
    # Corrige les problèmes d'images QCM Multichoix
    print("=== Correction des problèmes d'images QCM Multichoix ===\n")
    
    # 1. Créer les répertoires nécessaires
    ensure_directory_exists('static/exercises/qcm_multichoix')
    ensure_directory_exists('static/uploads/qcm_multichoix')
    ensure_directory_exists(BACKUP_DIR)
    
    # 2. Sauvegarder la base de données
    backup_path = backup_database()
    
    # 3. Connexion à la base de données
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        logger.info("Connexion à la base de données réussie")
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        return
    
    # 4. Récupérer tous les exercices QCM Multichoix
    try:
        cursor.execute("SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm_multichoix'")
        exercises = cursor.fetchall()
        logger.info(f"{len(exercises)} exercices QCM Multichoix trouvés")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des exercices QCM Multichoix: {e}")
        return
    
    # 5. Traiter chaque exercice
    fixed_count = 0
    for exercise_id, title, content_json, db_image_path in exercises:
        print(f"\nTraitement de l'exercice #{exercise_id}: {title}")
        
        try:
            # Déterminer le chemin d'image à utiliser
            image_path = db_image_path
            source = "image_path"
            
            if not image_path:
                # Vérifier dans le contenu JSON
                content = json.loads(content_json) if content_json else {}
                image_path = content.get('image', '')
                source = "content.image"
            
            if not image_path:
                print(f"  Pas d'image définie pour cet exercice")
                continue
            
            print(f"  Chemin d'image actuel ({source}): {image_path}")
            
            # Extraire le nom du fichier
            filename = os.path.basename(image_path)
            
            # Vérifier si l'image existe au chemin attendu
            expected_path = image_path
            if expected_path.startswith('/'):
                expected_path = expected_path[1:]
            
            if os.path.exists(expected_path):
                print(f"  ✅ L'image existe déjà au bon emplacement")
                continue
            
            # Rechercher l'image dans les chemins alternatifs
            alt_path = find_image_in_alternative_paths(filename)
            
            if alt_path:
                # Copier l'image vers le bon emplacement
                target_path = 'static/uploads/qcm_multichoix/' + filename
                shutil.copy2(alt_path, target_path)
                print(f"  ✅ Image copiée de {alt_path} vers {target_path}")
                
                # Mettre à jour le chemin dans la base de données
                new_path = '/static/uploads/qcm_multichoix/' + filename
                
                if source == "image_path":
                    cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", (new_path, exercise_id))
                else:
                    # Mettre à jour le champ image dans le contenu JSON
                    content = json.loads(content_json)
                    content['image'] = new_path
                    cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (json.dumps(content), exercise_id))
                
                conn.commit()
                print(f"  ✅ Chemin d'image mis à jour dans la base de données: {new_path}")
                fixed_count += 1
            else:
                print(f"  ❌ Image introuvable dans tous les chemins alternatifs")
        except Exception as e:
            print(f"  ❌ Erreur lors du traitement: {e}")
    
    # 6. Conclusion
    print("\n=== Résumé ===")
    print(f"Base de données sauvegardée: {backup_path}")
    print(f"{fixed_count} exercices QCM Multichoix corrigés sur {len(exercises)}")
    print("Opération terminée.")

if __name__ == "__main__":
    fix_qcm_multichoix_images()
