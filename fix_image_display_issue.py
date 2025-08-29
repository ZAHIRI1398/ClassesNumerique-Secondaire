#!/usr/bin/env python3
"""
Script pour corriger le problème d'affichage des images après création/modification d'exercices
"""

import os
import sys
import json
import glob
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Exercise
from app import app

def find_actual_image_files():
    """Trouver tous les fichiers d'images réellement présents dans static/uploads"""
    
    uploads_dir = Path("static/uploads")
    image_files = {}
    
    # Extensions d'images supportées
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.webp']
    
    for ext in image_extensions:
        # Recherche récursive dans tous les sous-dossiers
        for file_path in uploads_dir.rglob(ext):
            if file_path.is_file() and file_path.stat().st_size > 0:  # Ignorer les fichiers vides
                filename = file_path.name
                relative_path = str(file_path.relative_to(Path(".")))
                # Convertir en chemin web avec /
                web_path = "/" + relative_path.replace("\\", "/")
                image_files[filename] = web_path
    
    return image_files

def analyze_broken_images():
    """Analyser les images cassées et proposer des corrections"""
    
    print("=== ANALYSE DES IMAGES CASSEES ===\n")
    
    # Trouver tous les fichiers d'images disponibles
    available_images = find_actual_image_files()
    print(f"Fichiers d'images disponibles: {len(available_images)}")
    
    with app.app_context():
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        broken_images = []
        fixable_images = []
        
        for ex in exercises:
            db_path = ex.image_path
            
            # Extraire le nom du fichier depuis le chemin DB
            if '/' in db_path:
                filename = db_path.split('/')[-1]
            else:
                filename = db_path
            
            # Vérifier si le fichier existe dans notre liste
            if filename in available_images:
                actual_path = available_images[filename]
                if db_path != actual_path:
                    fixable_images.append((ex.id, ex.title, db_path, actual_path))
                    print(f"REPARABLE - ID {ex.id}: {ex.title[:40]}...")
                    print(f"  DB: {db_path}")
                    print(f"  Reel: {actual_path}")
                    print()
            else:
                broken_images.append((ex.id, ex.title, db_path, filename))
                print(f"CASSE - ID {ex.id}: {ex.title[:40]}...")
                print(f"  DB: {db_path}")
                print(f"  Fichier recherche: {filename}")
                print()
        
        print(f"\nRESUME:")
        print(f"Images reparables: {len(fixable_images)}")
        print(f"Images cassees: {len(broken_images)}")
        
        return fixable_images, broken_images

def fix_image_paths(dry_run=True):
    """Corriger les chemins d'images cassés"""
    
    print("=== CORRECTION DES CHEMINS D'IMAGES ===\n")
    
    if dry_run:
        print("MODE SIMULATION\n")
    else:
        print("MODE CORRECTION\n")
    
    available_images = find_actual_image_files()
    
    with app.app_context():
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        corrections = []
        
        for ex in exercises:
            db_path = ex.image_path
            
            # Extraire le nom du fichier
            if '/' in db_path:
                filename = db_path.split('/')[-1]
            else:
                filename = db_path
            
            # Chercher le fichier réel
            if filename in available_images:
                correct_path = available_images[filename]
                if db_path != correct_path:
                    corrections.append((ex.id, ex.title, db_path, correct_path))
                    
                    if not dry_run:
                        ex.image_path = correct_path
        
        if corrections:
            print(f"Corrections a effectuer: {len(corrections)}\n")
            for ex_id, title, old_path, new_path in corrections:
                print(f"ID {ex_id}: {title[:40]}...")
                print(f"  {old_path} -> {new_path}")
                print()
        
        if not dry_run and corrections:
            db.session.commit()
            print(f"{len(corrections)} chemins corriges!")
        
        return corrections

def check_zero_byte_files():
    """Identifier et signaler les fichiers de taille 0"""
    
    print("=== FICHIERS DE TAILLE 0 ===\n")
    
    uploads_dir = Path("static/uploads")
    zero_byte_files = []
    
    for file_path in uploads_dir.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size == 0:
            zero_byte_files.append(str(file_path))
    
    if zero_byte_files:
        print("Fichiers vides detectes (probleme d'upload):")
        for file_path in zero_byte_files:
            print(f"  {file_path}")
        print(f"\nTotal: {len(zero_byte_files)} fichiers vides")
        print("Ces fichiers doivent etre re-uploades.")
    else:
        print("Aucun fichier vide detecte.")
    
    return zero_byte_files

def main():
    """Fonction principale"""
    
    print("DIAGNOSTIC ET CORRECTION DES IMAGES CASSEES\n")
    
    # 1. Vérifier les fichiers de taille 0
    zero_files = check_zero_byte_files()
    
    # 2. Analyser les images cassées
    fixable, broken = analyze_broken_images()
    
    # 3. Proposer des corrections
    corrections = fix_image_paths(dry_run=True)
    
    print("\n=== RESUME FINAL ===")
    print(f"Fichiers vides (0 bytes): {len(zero_files)}")
    print(f"Images reparables: {len(fixable)}")
    print(f"Images definitivement cassees: {len(broken)}")
    print(f"Corrections automatiques possibles: {len(corrections)}")
    
    if corrections:
        print("\nPour appliquer les corrections automatiques:")
        print("python fix_image_display_issue.py --fix")
    
    if zero_files:
        print("\nACTIONS REQUISES:")
        print("1. Re-uploader les fichiers vides detectes")
        print("2. Executer les corrections automatiques")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        # Mode correction
        with app.app_context():
            fix_image_paths(dry_run=False)
    else:
        # Mode diagnostic
        main()
