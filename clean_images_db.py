#!/usr/bin/env python3
"""
Script direct pour nettoyer les images de la base de données
Sans dépendances Flask pour éviter les imports circulaires
"""

import sqlite3
import json
import os

def clean_images_database():
    """Nettoyer toutes les références d'images dans la base de données"""
    print("Nettoyage des images dans la base de donnees...")
    
    # Connexion directe à SQLite
    conn = sqlite3.connect('classes_numeriques.db')
    cursor = conn.cursor()
    
    try:
        # Vérifier si la table exercise existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercise'")
        if not cursor.fetchone():
            print("Table 'exercise' non trouvee. Verifiez le nom de la base de donnees.")
            return False
        
        # Compter les exercices avec images
        cursor.execute("SELECT COUNT(*) FROM exercise WHERE image_path IS NOT NULL")
        exercises_with_images = cursor.fetchone()[0]
        print(f"Exercices avec image_path: {exercises_with_images}")
        
        # Supprimer toutes les références image_path
        cursor.execute("UPDATE exercise SET image_path = NULL WHERE image_path IS NOT NULL")
        updated_count = cursor.rowcount
        print(f"Champs image_path nettoyes: {updated_count}")
        
        # Nettoyer les contenus JSON
        cursor.execute("SELECT id, content FROM exercise WHERE content IS NOT NULL AND content != ''")
        exercises_with_content = cursor.fetchall()
        content_updated = 0
        
        for exercise_id, content_str in exercises_with_content:
            try:
                content = json.loads(content_str)
                if isinstance(content, dict):
                    updated = False
                    
                    # Supprimer les clés d'images communes
                    image_keys = ['image', 'main_image', 'exercise_image']
                    for key in image_keys:
                        if key in content:
                            del content[key]
                            updated = True
                    
                    # Nettoyer les images dans les cartes (flashcards)
                    if 'cards' in content and isinstance(content['cards'], list):
                        for card in content['cards']:
                            if isinstance(card, dict) and 'image' in card:
                                del card['image']
                                updated = True
                    
                    # Nettoyer les images dans les paires
                    if 'pairs' in content and isinstance(content['pairs'], list):
                        for pair in content['pairs']:
                            if isinstance(pair, dict):
                                for side in ['left', 'right']:
                                    if side in pair and isinstance(pair[side], dict):
                                        if pair[side].get('type') == 'image':
                                            pair[side]['type'] = 'text'
                                            pair[side]['content'] = ''
                                            updated = True
                    
                    if updated:
                        new_content = json.dumps(content)
                        cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (new_content, exercise_id))
                        content_updated += 1
                        
            except json.JSONDecodeError:
                continue
        
        # Sauvegarder les changements
        conn.commit()
        
        if content_updated > 0:
            print(f"Contenus JSON nettoyes: {content_updated}")
        
        print("Nettoyage termine avec succes!")
        return True
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_clean_directories():
    """Créer la structure de dossiers propre"""
    print("\nCreation de la structure de dossiers...")
    
    upload_dirs = [
        'static/uploads',
        'static/uploads/exercises',
        'static/uploads/exercises/qcm',
        'static/uploads/exercises/fill_in_blanks', 
        'static/uploads/exercises/flashcards',
        'static/uploads/exercises/pairs',
        'static/uploads/exercises/image_labeling',
        'static/uploads/exercises/legend',
        'static/uploads/exercises/word_placement',
        'static/uploads/exercises/underline_words'
    ]
    
    created_count = 0
    for directory in upload_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            created_count += 1
        
        # Créer .gitkeep
        gitkeep_path = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write('# Keep this directory in git\n')
    
    print(f"Dossiers crees/verifies: {len(upload_dirs)}")
    print("Structure propre etablie!")

def show_final_stats():
    """Afficher les statistiques finales"""
    print("\nStatistiques finales:")
    
    conn = sqlite3.connect('classes_numeriques.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM exercise")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM exercise WHERE image_path IS NOT NULL")
        with_images = cursor.fetchone()[0]
        
        print(f"   Total exercices: {total}")
        print(f"   Avec images: {with_images}")
        print(f"   Sans images: {total - with_images}")
        
    except Exception as e:
        print(f"Erreur statistiques: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("NETTOYAGE COMPLET DU SYSTEME D'IMAGES")
    print("=" * 50)
    
    if clean_images_database():
        create_clean_directories()
        show_final_stats()
        
        print("\n" + "=" * 50)
        print("NETTOYAGE TERMINE AVEC SUCCES!")
        print("Vous pouvez maintenant ajouter des images proprement.")
        print("=" * 50)
    else:
        print("\nECHEC DU NETTOYAGE!")
