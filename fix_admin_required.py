#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour corriger l'erreur 'admin_required' non défini dans app.py
Ce script ajoute la définition du décorateur admin_required dans app.py
"""

import os
import sys
import re
from datetime import datetime

def backup_file(file_path):
    """Crée une sauvegarde du fichier"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    
    try:
        with open(file_path, "r", encoding="utf-8") as source:
            content = source.read()
        
        with open(backup_path, "w", encoding="utf-8") as target:
            target.write(content)
        
        print(f"Sauvegarde créée: {backup_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {e}")
        return False

def add_admin_required_decorator():
    """Ajoute le décorateur admin_required dans app.py"""
    file_path = "app.py"
    
    # Créer une sauvegarde
    if not backup_file(file_path):
        print("Impossible de créer une sauvegarde. Opération annulée.")
        return False
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Définition du décorateur admin_required à ajouter
        admin_required_code = """
# Décorateur pour vérifier si l'utilisateur est administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Accès refusé. Vous devez être administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
"""
        
        # Chercher où ajouter le décorateur (après l'import de wraps et avant la première utilisation)
        # Vérifier si functools.wraps est déjà importé
        if "from functools import wraps" not in content:
            # Ajouter l'import de wraps après les autres imports
            content = re.sub(
                r"(from flask_login import .*?\n)",
                r"\1from functools import wraps\n",
                content,
                flags=re.DOTALL
            )
        
        # Ajouter le décorateur après la définition de login_required
        pattern = r"(def login_required\(f\):.*?return decorated_function\n)"
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(
                pattern,
                r"\1\n" + admin_required_code,
                content,
                flags=re.DOTALL
            )
        else:
            # Si login_required n'est pas trouvé, ajouter après les imports
            content = re.sub(
                r"(from flask_login import .*?\n)",
                r"\1\n" + admin_required_code,
                content,
                flags=re.DOTALL
            )
        
        # Écrire le contenu modifié
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        
        print("✅ Le décorateur admin_required a été ajouté avec succès dans app.py")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de la modification de app.py: {e}")
        return False

if __name__ == "__main__":
    print("=== Correction de l'erreur 'admin_required' non défini ===\n")
    success = add_admin_required_decorator()
    
    if success:
        print("\nLa correction a été appliquée avec succès.")
        print("Vous pouvez maintenant démarrer l'application avec 'python app.py'")
    else:
        print("\nLa correction a échoué. Veuillez vérifier les erreurs ci-dessus.")
