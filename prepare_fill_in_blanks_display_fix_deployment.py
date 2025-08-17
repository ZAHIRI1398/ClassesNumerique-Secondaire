#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de préparation au déploiement de la correction pour l'affichage des blancs multiples
dans les exercices de type fill_in_blanks.

Ce script:
1. Crée une sauvegarde des fichiers modifiés
2. Vérifie que les modifications sont bien présentes
3. Prépare un résumé des modifications pour le commit
"""

import os
import sys
import json
import shutil
import datetime
from pathlib import Path

# Configuration
APP_PATH = Path(__file__).parent / "app.py"
TEMPLATE_PATH = Path(__file__).parent / "templates" / "exercise_types" / "fill_in_blanks.html"
BACKUP_DIR = Path(__file__).parent / f"backup_fill_in_blanks_display_fix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Fonction pour créer des sauvegardes
def create_backup(file_path, backup_dir):
    """Cree une sauvegarde du fichier specifie dans le repertoire de sauvegarde."""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, os.path.basename(file_path))
    shutil.copy2(file_path, backup_path)
    print(f"Sauvegarde creee: {backup_path}")
    return backup_path

# Fonction pour vérifier les modifications dans app.py
def check_app_py_modifications(file_path):
    """Verifie que les modifications necessaires sont presentes dans app.py."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifier la presence de la recuperation des reponses utilisateur
    has_user_answers_retrieval = "user_answers = {}" in content and "attempt.feedback" in content
    
    # Verifier le passage des reponses au template
    has_template_passing = "user_answers=user_answers" in content
    
    return has_user_answers_retrieval and has_template_passing

# Fonction pour vérifier les modifications dans le template
def check_template_modifications(file_path):
    """Verifie que les modifications necessaires sont presentes dans le template."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifier la presence de l'attribut value avec user_answers
    has_value_attribute = 'value="{{ user_answers.get' in content
    
    return has_value_attribute

# Fonction principale
def main():
    print("=== Preparation au deploiement de la correction pour l'affichage des blancs multiples ===")
    
    # 1. Creer des sauvegardes
    print("\n1. Creation des sauvegardes...")
    app_backup = create_backup(APP_PATH, BACKUP_DIR)
    template_backup = create_backup(TEMPLATE_PATH, BACKUP_DIR)
    
    # 2. Verifier les modifications
    print("\n2. Verification des modifications...")
    
    app_modified = check_app_py_modifications(APP_PATH)
    template_modified = check_template_modifications(TEMPLATE_PATH)
    
    if app_modified and template_modified:
        print("[OK] Toutes les modifications necessaires sont presentes.")
    else:
        print("[ERREUR] Certaines modifications sont manquantes:")
        if not app_modified:
            print("   - Les modifications dans app.py sont incompletes ou absentes.")
        if not template_modified:
            print("   - Les modifications dans le template fill_in_blanks.html sont incompletes ou absentes.")
        print("\nVeuillez verifier les fichiers et reessayer.")
        return 1
    
    # 3. Preparer le resume pour le commit
    print("\n3. Resume des modifications pour le commit:")
    commit_message = """
Fix: Correction de l'affichage des blancs multiples dans les exercices fill_in_blanks

Cette correction resout le probleme ou les deuxiemes blancs (et suivants) dans une meme ligne 
n'etaient pas correctement affiches apres la soumission d'un exercice de type "texte a trous".

Modifications:
- Ajout de la recuperation des reponses utilisateur dans la fonction view_exercise
- Passage des reponses utilisateur au template
- Ajout de l'attribut value aux champs de saisie pour afficher les reponses precedentes

Cette correction ameliore l'experience utilisateur en permettant aux etudiants de voir 
leurs reponses precedentes apres soumission, facilitant ainsi la revision et la correction.
"""
    print(commit_message)
    
    # 4. Instructions pour le deploiement
    print("\n4. Instructions pour le deploiement:")
    print("""
Pour déployer cette correction:

1. Verifiez une derniere fois les modifications avec un exercice de test
2. Commitez les modifications avec le message de commit fourni:
   git add app.py templates/exercise_types/fill_in_blanks.html
   git commit -m "Fix: Correction de l'affichage des blancs multiples dans les exercices fill_in_blanks"
3. Poussez les modifications vers le depot distant:
   git push origin main
4. Verifiez le deploiement sur Railway
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
