#!/usr/bin/env python3
"""
Script pour diagnostiquer et corriger les problèmes de chemins d'images incohérents
"""

import os
import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Exercise
from app import app

def analyze_image_paths():
    """Analyser tous les chemins d'images dans la base de données"""
    
    print("=== ANALYSE DES CHEMINS D'IMAGES ===\n")
    
    with app.app_context():
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        print(f"Nombre d'exercices avec images: {len(exercises)}\n")
        
        # Catégoriser les différents formats de chemins
        formats = {
            'static_uploads_slash': [],      # /static/uploads/filename
            'static_uploads_no_slash': [],   # static/uploads/filename
            'uploads_only': [],              # uploads/filename
            'other': []                      # autres formats
        }
        
        for ex in exercises:
            path = ex.image_path
            
            if path.startswith('/static/uploads/'):
                formats['static_uploads_slash'].append((ex.id, ex.title, path))
            elif path.startswith('static/uploads/'):
                formats['static_uploads_no_slash'].append((ex.id, ex.title, path))
            elif path.startswith('uploads/'):
                formats['uploads_only'].append((ex.id, ex.title, path))
            else:
                formats['other'].append((ex.id, ex.title, path))
        
        # Afficher les résultats
        for format_name, exercises_list in formats.items():
            if exercises_list:
                print(f"=== FORMAT: {format_name.upper()} ({len(exercises_list)} exercices) ===")
                for ex_id, title, path in exercises_list[:5]:  # Afficher les 5 premiers
                    print(f"  ID {ex_id}: {title[:50]}... -> {path}")
                if len(exercises_list) > 5:
                    print(f"  ... et {len(exercises_list) - 5} autres")
                print()
        
        return formats

def check_file_existence():
    """Vérifier quels fichiers d'images existent réellement"""
    
    print("=== VÉRIFICATION DE L'EXISTENCE DES FICHIERS ===\n")
    
    uploads_dir = Path("static/uploads")
    if not uploads_dir.exists():
        print(f"Dossier {uploads_dir} n'existe pas!")
        return
    
    with app.app_context():
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        existing_files = []
        missing_files = []
        
        for ex in exercises:
            path = ex.image_path
            
            # Normaliser le chemin pour vérifier l'existence
            if path.startswith('/static/uploads/'):
                filename = path.replace('/static/uploads/', '')
            elif path.startswith('static/uploads/'):
                filename = path.replace('static/uploads/', '')
            elif path.startswith('uploads/'):
                filename = path.replace('uploads/', '')
            else:
                filename = path
            
            file_path = uploads_dir / filename
            
            if file_path.exists():
                existing_files.append((ex.id, ex.title, path, str(file_path)))
            else:
                missing_files.append((ex.id, ex.title, path, str(file_path)))
        
        print(f"Fichiers existants: {len(existing_files)}")
        print(f"Fichiers manquants: {len(missing_files)}\n")
        
        if missing_files:
            print("=== FICHIERS MANQUANTS ===")
            for ex_id, title, db_path, expected_path in missing_files[:10]:
                print(f"  ID {ex_id}: {title[:40]}...")
                print(f"    DB: {db_path}")
                print(f"    Attendu: {expected_path}")
                print()
        
        return existing_files, missing_files

def fix_image_paths(dry_run=True):
    """Corriger les chemins d'images pour utiliser un format cohérent"""
    
    print("=== CORRECTION DES CHEMINS D'IMAGES ===\n")
    
    if dry_run:
        print("MODE SIMULATION (aucune modification ne sera effectuee)\n")
    else:
        print("MODE CORRECTION (les modifications seront appliquees)\n")
    
    with app.app_context():
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        
        corrections = []
        
        for ex in exercises:
            old_path = ex.image_path
            
            # Normaliser vers le format /static/uploads/filename
            if old_path.startswith('/static/uploads/'):
                # Déjà correct
                continue
            elif old_path.startswith('static/uploads/'):
                new_path = '/' + old_path
            elif old_path.startswith('uploads/'):
                new_path = '/static/' + old_path
            else:
                # Format non reconnu, essayer de deviner
                filename = os.path.basename(old_path)
                new_path = f'/static/uploads/{filename}'
            
            corrections.append((ex.id, ex.title, old_path, new_path))
            
            if not dry_run:
                ex.image_path = new_path
        
        if corrections:
            print(f"Corrections à effectuer: {len(corrections)}\n")
            for ex_id, title, old_path, new_path in corrections[:10]:
                print(f"  ID {ex_id}: {title[:40]}...")
                print(f"    Ancien: {old_path}")
                print(f"    Nouveau: {new_path}")
                print()
            
            if len(corrections) > 10:
                print(f"  ... et {len(corrections) - 10} autres corrections")
        
        if not dry_run and corrections:
            db.session.commit()
            print(f"{len(corrections)} chemins d'images corriges!")
        
        return corrections

def main():
    """Fonction principale"""
    
    print("DIAGNOSTIC ET CORRECTION DES CHEMINS D'IMAGES\n")
    
    # 1. Analyser les formats actuels
    formats = analyze_image_paths()
    
    # 2. Vérifier l'existence des fichiers
    existing, missing = check_file_existence()
    
    # 3. Proposer des corrections (simulation)
    corrections = fix_image_paths(dry_run=True)
    
    print("\n=== RÉSUMÉ ===")
    print(f"Formats detectes: {len([f for f in formats.values() if f])}")
    print(f"Fichiers existants: {len(existing)}")
    print(f"Fichiers manquants: {len(missing)}")
    print(f"Corrections proposees: {len(corrections)}")
    
    if corrections:
        print("\nPour appliquer les corrections, executez:")
        print("python fix_image_paths_consistency.py --fix")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        # Mode correction
        with app.app_context():
            fix_image_paths(dry_run=False)
    else:
        # Mode diagnostic
        main()
