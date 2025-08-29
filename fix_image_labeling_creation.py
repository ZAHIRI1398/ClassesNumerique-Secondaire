"""
Script pour corriger le problème d'affichage des images dans les exercices de type image_labeling.
Ce script modifie le code de création des exercices pour normaliser les chemins d'images.
"""

import os
import json
from flask import Flask, current_app, url_for, redirect, request, flash
import time

def normalize_image_path(path):
    """
    Normalise un chemin d'image pour s'assurer qu'il commence par /static/uploads/
    """
    if not path:
        return path
        
    # Supprimer le préfixe /static/ s'il existe déjà
    if path.startswith('/static/'):
        path = path[8:]  # Enlever '/static/'
        
    # Supprimer le préfixe static/ s'il existe
    if path.startswith('static/'):
        path = path[7:]  # Enlever 'static/'
        
    # S'assurer que le chemin commence par uploads/
    if not path.startswith('uploads/'):
        if '/' in path:
            # Si le chemin contient déjà un dossier, remplacer ce dossier par uploads
            path = 'uploads/' + path.split('/', 1)[1]
        else:
            # Sinon, ajouter le préfixe uploads/
            path = 'uploads/' + path
            
    # Ajouter le préfixe /static/
    return '/static/' + path

def fix_image_labeling_exercise_creation(app_file_path):
    """
    Modifie le code de création des exercices image_labeling pour normaliser les chemins d'images.
    """
    with open(app_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Corriger le chemin de l'image principale dans la création d'exercices image_labeling
    # Remplacer: main_image_path = f'uploads/{unique_filename}'
    # Par: main_image_path = f'/static/uploads/{unique_filename}'
    content = content.replace(
        "main_image_path = f'uploads/{unique_filename}'",
        "main_image_path = f'/static/uploads/{unique_filename}'"
    )
    
    # 2. Ajouter un paramètre de timestamp pour éviter les problèmes de cache
    # Rechercher la redirection après création d'exercice
    redirect_pattern = "return redirect(url_for('exercise.exercise_library'))"
    timestamp_redirect = "return redirect(url_for('exercise.exercise_library', _t=int(time.time())))"
    
    # Vérifier si l'import time existe déjà
    if "import time" not in content:
        # Ajouter l'import time après les autres imports
        content = content.replace(
            "import json",
            "import json\nimport time"
        )
    
    # Remplacer la redirection
    content = content.replace(redirect_pattern, timestamp_redirect)
    
    # Écrire le fichier modifié
    with open(app_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"[SUCCES] Le fichier {app_file_path} a ete modifie avec succes.")
    print("[SUCCES] Les chemins d'images pour les exercices image_labeling sont maintenant normalises.")
    print("[SUCCES] Un parametre de timestamp a ete ajoute pour eviter les problemes de cache.")

def create_fix_script():
    """
    Crée un script autonome pour appliquer les corrections.
    """
    script_content = """
import os
import sys

def fix_image_labeling_creation():
    # Chemin vers le fichier app.py
    app_file_path = 'app.py'
    
    if not os.path.exists(app_file_path):
        print(f"[ERREUR] Le fichier {app_file_path} n'existe pas.")
        return False
    
    try:
        from fix_image_labeling_creation import fix_image_labeling_exercise_creation
        fix_image_labeling_exercise_creation(app_file_path)
        print("[SUCCES] Correction appliquee avec succes!")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'application de la correction: {e}")
        return False

if __name__ == "__main__":
    print("[INFO] Application de la correction pour l'affichage des images dans les exercices image_labeling...")
    success = fix_image_labeling_creation()
    if success:
        print("[SUCCES] Correction terminee avec succes.")
    else:
        print("[ERREUR] La correction a echoue.")
        sys.exit(1)
    """
    
    with open('apply_image_labeling_fix.py', 'w', encoding='utf-8') as file:
        file.write(script_content)
    
    print("[SUCCES] Script d'application de la correction cree: apply_image_labeling_fix.py")

if __name__ == "__main__":
    # Exemple d'utilisation
    print("Ce script doit être importé et utilisé dans un autre script.")
    print("Exemple d'utilisation:")
    print("from fix_image_labeling_creation import fix_image_labeling_exercise_creation")
    print("fix_image_labeling_exercise_creation('app.py')")
    
    # Créer le script d'application
    create_fix_script()
