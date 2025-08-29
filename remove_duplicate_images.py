"""
Script pour détecter et supprimer les doublons d'images tout en préservant les références
dans la base de données.

Ce script:
1. Identifie les images dupliquées (même contenu mais noms différents)
2. Détermine quelle version conserver (priorité à la version normalisée)
3. Met à jour les références dans la base de données
4. Supprime les fichiers dupliqués
"""

import os
import re
import sys
import logging
import hashlib
import shutil
from flask import Flask
from sqlalchemy import create_engine, text
from utils.image_path_handler import normalize_filename, normalize_image_path

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('remove_duplicate_images.log'), 
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Créer une application Flask pour le contexte
app = Flask(__name__)

# Chemins des répertoires d'images à vérifier
IMAGE_DIRECTORIES = [
    "static/uploads/exercises/qcm",
    "static/uploads/exercises/flashcards",
    "static/uploads/exercises/word_placement",
    "static/uploads/exercises/image_labeling",
    "static/uploads/exercises/legend",
    "static/uploads/exercises",
    "static/exercises/qcm",
    "static/exercises/flashcards",
    "static/exercises/word_placement",
    "static/exercises/image_labeling",
    "static/exercises/legend",
    "static/exercises"
]

def get_file_hash(file_path):
    """
    Calcule le hash MD5 d'un fichier pour identifier les doublons
    """
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        return file_hash.hexdigest()
    except Exception as e:
        logger.error(f"Erreur lors du calcul du hash pour {file_path}: {str(e)}")
        return None

def find_duplicate_images():
    """
    Trouve les images dupliquées dans les répertoires spécifiés
    
    Returns:
        dict: Dictionnaire avec les hash MD5 comme clés et les listes de chemins comme valeurs
    """
    hash_dict = {}
    total_files = 0
    
    # Parcourir tous les répertoires d'images
    for directory in IMAGE_DIRECTORIES:
        if not os.path.exists(directory):
            logger.warning(f"Le répertoire {directory} n'existe pas")
            continue
            
        logger.info(f"Analyse du répertoire {directory}")
        
        # Parcourir tous les fichiers du répertoire
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Vérifier si c'est un fichier image
            if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                total_files += 1
                
                # Calculer le hash du fichier
                file_hash = get_file_hash(file_path)
                if file_hash:
                    # Ajouter le chemin à la liste des fichiers avec ce hash
                    if file_hash in hash_dict:
                        hash_dict[file_hash].append(file_path)
                    else:
                        hash_dict[file_hash] = [file_path]
    
    # Filtrer pour ne garder que les hash avec plusieurs fichiers (doublons)
    duplicate_dict = {h: paths for h, paths in hash_dict.items() if len(paths) > 1}
    
    logger.info(f"Total des fichiers analysés: {total_files}")
    logger.info(f"Nombre de groupes de doublons trouvés: {len(duplicate_dict)}")
    
    return duplicate_dict

def choose_file_to_keep(file_paths):
    """
    Détermine quel fichier conserver parmi les doublons
    
    Stratégie:
    1. Préférer les fichiers avec noms normalisés
    2. Préférer les fichiers dans /static/uploads/ plutôt que /static/
    3. En cas d'égalité, garder le premier par ordre alphabétique
    
    Args:
        file_paths (list): Liste des chemins de fichiers dupliqués
        
    Returns:
        tuple: (fichier à conserver, fichiers à supprimer)
    """
    if not file_paths:
        return None, []
    
    # Si un seul fichier, le conserver
    if len(file_paths) == 1:
        return file_paths[0], []
    
    # Calculer un score pour chaque fichier
    scored_files = []
    for path in file_paths:
        score = 0
        filename = os.path.basename(path)
        normalized_filename = normalize_filename(filename)
        
        # Si le nom est déjà normalisé, donner un bonus
        if filename == normalized_filename:
            score += 10
            
        # Préférer les fichiers dans /uploads/
        if "/uploads/" in path:
            score += 5
            
        # Préférer les chemins plus courts (moins de segments)
        segments = path.count("/")
        score -= segments
        
        scored_files.append((path, score))
    
    # Trier par score décroissant
    scored_files.sort(key=lambda x: x[1], reverse=True)
    
    # Le fichier avec le meilleur score est à conserver
    file_to_keep = scored_files[0][0]
    files_to_remove = [f[0] for f in scored_files[1:]]
    
    return file_to_keep, files_to_remove

def update_database_references(old_paths, new_path):
    """
    Met à jour les références dans la base de données
    
    Args:
        old_paths (list): Liste des chemins à remplacer
        new_path (str): Nouveau chemin à utiliser
    """
    try:
        # Charger la configuration de la base de données depuis config.py
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config import Config
        
        # Créer une connexion à la base de données
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        
        # Normaliser les chemins pour la recherche en base de données
        normalized_old_paths = []
        for path in old_paths:
            # Préparer différentes variantes du chemin pour la recherche
            if path.startswith('/'):
                normalized_old_paths.append(path)
                normalized_old_paths.append(path[1:])
            else:
                normalized_old_paths.append(f"/{path}")
                normalized_old_paths.append(path)
        
        # Normaliser le nouveau chemin
        if new_path.startswith('/'):
            normalized_new_path = new_path
        else:
            normalized_new_path = f"/{new_path}"
        
        # Mettre à jour les références dans la table Exercise
        for old_path in normalized_old_paths:
            query = text("""
                UPDATE exercise 
                SET image_path = :new_path 
                WHERE image_path = :old_path
            """)
            result = connection.execute(query, {"new_path": normalized_new_path, "old_path": old_path})
            if result.rowcount > 0:
                logger.info(f"Mise à jour de {result.rowcount} références dans exercise.image_path: {old_path} -> {normalized_new_path}")
        
        # Mettre à jour les références dans le contenu JSON des exercices
        query = text("""
            SELECT id, content FROM exercise WHERE content IS NOT NULL
        """)
        exercises = connection.execute(query).fetchall()
        
        for exercise_id, content in exercises:
            updated = False
            
            # Vérifier si le contenu contient une des anciennes références
            for old_path in normalized_old_paths:
                if old_path in content:
                    # Remplacer l'ancienne référence par la nouvelle
                    updated_content = content.replace(old_path, normalized_new_path)
                    if updated_content != content:
                        update_query = text("""
                            UPDATE exercise 
                            SET content = :content 
                            WHERE id = :id
                        """)
                        connection.execute(update_query, {"content": updated_content, "id": exercise_id})
                        logger.info(f"Mise à jour du contenu JSON de l'exercice {exercise_id}: {old_path} -> {normalized_new_path}")
                        updated = True
                        content = updated_content
            
        connection.close()
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la base de données: {str(e)}")

def remove_duplicate_files(files_to_remove):
    """
    Supprime les fichiers dupliqués
    
    Args:
        files_to_remove (list): Liste des chemins de fichiers à supprimer
        
    Returns:
        int: Nombre de fichiers supprimés
    """
    count = 0
    for file_path in files_to_remove:
        try:
            # Créer un répertoire de sauvegarde si nécessaire
            backup_dir = "static/backup_duplicates"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copier le fichier dans le répertoire de sauvegarde
            filename = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, filename)
            
            # Si le fichier existe déjà dans le répertoire de sauvegarde, ajouter un suffixe
            if os.path.exists(backup_path):
                base, ext = os.path.splitext(filename)
                backup_path = os.path.join(backup_dir, f"{base}_{count}{ext}")
            
            shutil.copy2(file_path, backup_path)
            logger.info(f"Fichier sauvegardé: {file_path} -> {backup_path}")
            
            # Supprimer le fichier original
            os.remove(file_path)
            logger.info(f"Fichier supprimé: {file_path}")
            count += 1
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de {file_path}: {str(e)}")
    
    return count

def process_duplicates():
    """
    Traite les doublons d'images
    """
    # Trouver les doublons
    duplicate_dict = find_duplicate_images()
    
    total_removed = 0
    total_groups = len(duplicate_dict)
    
    # Traiter chaque groupe de doublons
    for hash_value, file_paths in duplicate_dict.items():
        logger.info(f"Traitement du groupe de doublons: {file_paths}")
        
        # Choisir le fichier à conserver
        file_to_keep, files_to_remove = choose_file_to_keep(file_paths)
        
        if file_to_keep and files_to_remove:
            logger.info(f"Fichier à conserver: {file_to_keep}")
            logger.info(f"Fichiers à supprimer: {files_to_remove}")
            
            # Mettre à jour les références dans la base de données
            update_database_references(files_to_remove, file_to_keep)
            
            # Supprimer les fichiers dupliqués
            removed = remove_duplicate_files(files_to_remove)
            total_removed += removed
    
    logger.info(f"Traitement terminé: {total_removed} fichiers dupliqués supprimés sur {total_groups} groupes")
    return total_groups, total_removed

if __name__ == "__main__":
    with app.app_context():
        logger.info("Démarrage du script de suppression des doublons d'images")
        total_groups, total_removed = process_duplicates()
        logger.info(f"Script terminé. {total_removed} fichiers dupliqués supprimés sur {total_groups} groupes")
