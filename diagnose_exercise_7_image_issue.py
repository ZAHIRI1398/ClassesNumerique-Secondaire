#!/usr/bin/env python3
"""
Script pour diagnostiquer le problème d'affichage d'image de l'exercice 7
"""

import os
import sys
import json

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Exercise
from app import app

def diagnose_exercise_7_image():
    """Diagnostiquer le problème d'image de l'exercice 7"""
    
    print("=== DIAGNOSTIC IMAGE EXERCICE 7 ===\n")
    
    with app.app_context():
        # Récupérer l'exercice
        exercise = Exercise.query.get(7)
        if not exercise:
            print("Exercice 7 non trouve!")
            return
        
        print(f"ETAT ACTUEL DE L'EXERCICE 7")
        print(f"Titre: {exercise.title}")
        print(f"Image path dans DB: {exercise.image_path}")
        print()
        
        # Analyser le contenu JSON
        if exercise.content:
            try:
                content = json.loads(exercise.content)
                print(f"Image dans le JSON: {content.get('image', 'Aucune')}")
            except:
                print("Erreur parsing JSON")
        print()
        
        # Vérifier les fichiers sur disque
        print("VERIFICATION DES FICHIERS:")
        
        # Vérifier l'ancienne image
        if exercise.image_path:
            old_image_path = exercise.image_path.replace('/static/uploads/', '').replace('static/uploads/', '')
            old_image_file = f"static/uploads/{old_image_path}"
            
            print(f"Ancienne image: {old_image_file}")
            if os.path.exists(old_image_file):
                size = os.path.getsize(old_image_file)
                print(f"  Existe: OUI ({size} bytes)")
                if size == 0:
                    print("  PROBLEME: Fichier vide (0 bytes)")
            else:
                print(f"  Existe: NON")
        
        # Chercher les nouvelles images potentielles
        upload_dir = "static/uploads"
        if os.path.exists(upload_dir):
            print(f"\nFichiers dans {upload_dir}:")
            files = os.listdir(upload_dir)
            recent_files = []
            
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_path = os.path.join(upload_dir, file)
                    size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    
                    print(f"  {file}: {size} bytes (modifie: {mtime})")
                    
                    # Fichiers récents (dernières 24h)
                    import time
                    if time.time() - mtime < 86400:  # 24h
                        recent_files.append((file, size, mtime))
            
            if recent_files:
                print(f"\nFichiers récents (dernières 24h):")
                recent_files.sort(key=lambda x: x[2], reverse=True)  # Trier par date
                for file, size, mtime in recent_files:
                    import datetime
                    date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  {file}: {size} bytes ({date_str})")
        
        print(f"\nSUGGESTIONS DE CORRECTION:")
        print(f"1. Supprimer l'ancienne image corrompue de 0 bytes")
        print(f"2. Mettre à jour le chemin d'image dans la base de données")
        print(f"3. Vérifier que la nouvelle image est correctement sauvegardée")

def fix_exercise_7_image():
    """Corriger l'image de l'exercice 7"""
    
    print("\n=== CORRECTION IMAGE EXERCICE 7 ===\n")
    
    with app.app_context():
        exercise = Exercise.query.get(7)
        if not exercise:
            print("Exercice 7 non trouve!")
            return
        
        # Supprimer l'ancienne image corrompue
        if exercise.image_path:
            old_image_path = exercise.image_path.replace('/static/uploads/', '').replace('static/uploads/', '')
            old_image_file = f"static/uploads/{old_image_path}"
            
            if os.path.exists(old_image_file):
                size = os.path.getsize(old_image_file)
                if size == 0:
                    print(f"Suppression de l'ancienne image corrompue: {old_image_file}")
                    os.remove(old_image_file)
                    print("  Supprimee avec succes")
        
        # Chercher la nouvelle image la plus récente
        upload_dir = "static/uploads"
        if os.path.exists(upload_dir):
            files = os.listdir(upload_dir)
            recent_images = []
            
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_path = os.path.join(upload_dir, file)
                    size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    
                    # Fichiers récents et non vides
                    import time
                    if time.time() - mtime < 86400 and size > 0:  # 24h et non vide
                        recent_images.append((file, size, mtime))
            
            if recent_images:
                # Prendre l'image la plus récente
                recent_images.sort(key=lambda x: x[2], reverse=True)
                newest_image = recent_images[0][0]
                
                print(f"Nouvelle image detectee: {newest_image}")
                
                # Mettre à jour la base de données
                new_image_path = f"/static/uploads/{newest_image}"
                exercise.image_path = new_image_path
                
                # Mettre à jour le JSON aussi
                if exercise.content:
                    try:
                        content = json.loads(exercise.content)
                        content['image'] = new_image_path
                        exercise.content = json.dumps(content)
                        print(f"JSON mis a jour avec: {new_image_path}")
                    except:
                        print("Erreur mise a jour JSON")
                
                db.session.commit()
                print(f"Base de donnees mise a jour: {new_image_path}")
                print("CORRECTION TERMINEE")
            else:
                print("Aucune nouvelle image trouvee")

if __name__ == "__main__":
    diagnose_exercise_7_image()
    print("\n" + "="*50)
    fix_exercise_7_image()
