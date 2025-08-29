#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import json
import shutil
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'fix_zero_byte_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)

# Chemins et configuration
DB_PATH = 'instance/app.db'
STATIC_DIR = 'static'
PLACEHOLDER_IMAGE = 'static/img/image_placeholder.png'  # Image par défaut à utiliser

def create_placeholder_if_needed():
    """Crée une image placeholder si elle n'existe pas"""
    os.makedirs(os.path.dirname(PLACEHOLDER_IMAGE), exist_ok=True)
    
    if not os.path.exists(PLACEHOLDER_IMAGE):
        # Créer une image placeholder simple
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (400, 300), color=(240, 240, 240))
            d = ImageDraw.Draw(img)
            d.text((150, 150), "Image non disponible", fill=(0, 0, 0))
            img.save(PLACEHOLDER_IMAGE)
            logging.info(f"Image placeholder créée: {PLACEHOLDER_IMAGE}")
        except ImportError:
            # Si PIL n'est pas disponible, créer un fichier texte
            with open(PLACEHOLDER_IMAGE, 'w') as f:
                f.write("Image placeholder")
            logging.info(f"Fichier placeholder créé: {PLACEHOLDER_IMAGE}")

def fix_exercise_image(exercise_id, conn=None):
    """Corrige l'image d'un exercice spécifique"""
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True
    
    cursor = conn.cursor()
    
    try:
        # Récupérer les données de l'exercice
        cursor.execute('SELECT id, title, exercise_type, image_path, content FROM exercise WHERE id = ?', (exercise_id,))
        result = cursor.fetchone()
        
        if not result:
            logging.error(f"Exercice ID {exercise_id} non trouvé")
            return False
        
        id, title, exercise_type, image_path, content_json = result
        
        # Analyser le contenu JSON
        try:
            content = json.loads(content_json) if content_json else {}
        except json.JSONDecodeError:
            content = {}
            logging.error(f"Erreur de décodage JSON pour l'exercice {id}")
        
        # Vérifier si l'image existe et a une taille de 0 octets
        image_to_check = image_path
        content_image = content.get('image')
        
        if image_to_check and os.path.exists(image_to_check.lstrip('/')):
            file_path = image_to_check.lstrip('/')
            if os.path.getsize(file_path) == 0:
                logging.info(f"Image de 0 octets détectée: {file_path}")
                
                # Remplacer par l'image placeholder
                normalized_placeholder = '/' + PLACEHOLDER_IMAGE.replace('\\', '/')
                
                # Mettre à jour exercise.image_path
                cursor.execute('UPDATE exercise SET image_path = ? WHERE id = ?', 
                              (normalized_placeholder, id))
                
                # Mettre à jour content['image']
                if content:
                    content['image'] = normalized_placeholder
                    cursor.execute('UPDATE exercise SET content = ? WHERE id = ?', 
                                  (json.dumps(content), id))
                
                conn.commit()
                logging.info(f"Exercice {id} mis à jour avec l'image placeholder")
                return True
        
        # Vérifier également content['image'] si différent de image_path
        if content_image and content_image != image_path and os.path.exists(content_image.lstrip('/')):
            file_path = content_image.lstrip('/')
            if os.path.getsize(file_path) == 0:
                logging.info(f"Image de contenu de 0 octets détectée: {file_path}")
                
                # Remplacer par l'image placeholder
                normalized_placeholder = '/' + PLACEHOLDER_IMAGE.replace('\\', '/')
                
                # Mettre à jour content['image']
                content['image'] = normalized_placeholder
                cursor.execute('UPDATE exercise SET content = ? WHERE id = ?', 
                              (json.dumps(content), id))
                
                # Mettre à jour exercise.image_path si vide
                if not image_path:
                    cursor.execute('UPDATE exercise SET image_path = ? WHERE id = ?', 
                                  (normalized_placeholder, id))
                
                conn.commit()
                logging.info(f"Contenu de l'exercice {id} mis à jour avec l'image placeholder")
                return True
        
        logging.info(f"Aucune image de 0 octets trouvée pour l'exercice {id}")
        return False
    
    except Exception as e:
        logging.error(f"Erreur lors de la correction de l'exercice {exercise_id}: {str(e)}")
        return False
    
    finally:
        if close_conn:
            conn.close()

def scan_all_exercises():
    """Analyse tous les exercices pour détecter et corriger les images de 0 octets"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Récupérer tous les IDs d'exercices
        cursor.execute('SELECT id FROM exercise')
        exercise_ids = [row[0] for row in cursor.fetchall()]
        
        fixed_count = 0
        for exercise_id in exercise_ids:
            if fix_exercise_image(exercise_id, conn):
                fixed_count += 1
        
        logging.info(f"Scan terminé. {fixed_count} exercices corrigés sur {len(exercise_ids)} analysés.")
        return fixed_count
    
    except Exception as e:
        logging.error(f"Erreur lors du scan des exercices: {str(e)}")
        return 0
    
    finally:
        conn.close()

def main():
    """Fonction principale"""
    print("Correction des images de 0 octets dans les exercices")
    logging.info("Démarrage du script de correction des images")
    
    # Créer l'image placeholder si nécessaire
    create_placeholder_if_needed()
    
    # Corriger l'exercice spécifique (ID 86)
    print("Correction de l'exercice ID 86...")
    if fix_exercise_image(86):
        print("[OK] Exercice ID 86 corrigé avec succès")
    else:
        print("[ERREUR] Aucune correction nécessaire ou erreur pour l'exercice ID 86")
    
    # Scanner automatiquement tous les exercices
    print("\nAnalyse de tous les exercices pour détecter les images de 0 octets...")
    fixed_count = scan_all_exercises()
    print(f"[OK] {fixed_count} exercices corrigés")
    
    print("\nTerminé. Consultez le fichier log pour plus de détails.")

if __name__ == "__main__":
    main()
